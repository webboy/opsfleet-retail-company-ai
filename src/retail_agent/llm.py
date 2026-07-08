"""LLM factory, retry/backoff, fallback providers, and per-turn call budget."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from retail_agent.config import Settings, get_settings

DEFAULT_MAX_LLM_CALLS = 8
DEFAULT_MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1.0
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "openrouter/auto"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2"
SUPPORTED_PROVIDERS = frozenset({"gemini", "openrouter", "ollama"})
ProviderName = Literal["gemini", "openrouter", "ollama"]


class BudgetExhaustedError(Exception):
    """Raised when the per-turn LLM call budget is exhausted."""


@dataclass
class CallBudget:
    max_calls: int = DEFAULT_MAX_LLM_CALLS
    used: int = 0

    def remaining(self) -> int:
        return max(0, self.max_calls - self.used)

    def can_consume(self, count: int = 1) -> bool:
        return self.used + count <= self.max_calls

    def consume(self, count: int = 1) -> None:
        if not self.can_consume(count):
            raise BudgetExhaustedError("LLM call budget exhausted for this turn.")
        self.used += count

    def to_dict(self) -> dict[str, int]:
        return {"max_calls": self.max_calls, "used": self.used}

    @classmethod
    def from_dict(cls, data: dict[str, int] | None) -> CallBudget:
        if not data:
            return cls()
        return cls(max_calls=data.get("max_calls", DEFAULT_MAX_LLM_CALLS), used=data.get("used", 0))


@dataclass
class FallbackChatModel:
    """Primary provider with optional transparent fallback on quota/outage."""

    primary: BaseChatModel
    fallback: BaseChatModel | None
    primary_provider: str
    fallback_provider: str | None = None
    fallback_count: int = 0
    last_fallback_provider: str | None = None
    last_primary_error: str | None = None

    def record_fallback_use(self, *, error: Exception) -> None:
        self.fallback_count += 1
        self.last_fallback_provider = self.fallback_provider
        self.last_primary_error = str(error)


def create_chat_model(settings: Settings | None = None) -> BaseChatModel | FallbackChatModel:
    settings = settings or get_settings()
    primary_name = _normalize_provider(settings.provider)
    primary = _create_provider_model(primary_name, settings)
    if not settings.fallback_provider:
        return primary
    fallback_name = _normalize_provider(settings.fallback_provider)
    fallback = _create_provider_model(fallback_name, settings)
    return FallbackChatModel(
        primary=primary,
        fallback=fallback,
        primary_provider=primary_name,
        fallback_provider=fallback_name,
    )


def _create_provider_model(provider: str, settings: Settings) -> BaseChatModel:
    normalized = _normalize_provider(provider)
    if normalized == "gemini":
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required when RETAIL_AGENT_PROVIDER=gemini.")
        return ChatGoogleGenerativeAI(
            model=settings.model,
            google_api_key=settings.google_api_key,
            temperature=0.1,
        )
    if normalized == "openrouter":
        if not settings.openrouter_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is required when using the openrouter provider."
            )
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
            base_url=OPENROUTER_BASE_URL,
            temperature=0.1,
        )
    if normalized == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_host,
            temperature=0.1,
        )
    raise ValueError(f"Unsupported LLM provider: {provider!r}")


def invoke_with_retry(
    llm: BaseChatModel | FallbackChatModel,
    messages: list[BaseMessage],
    budget: CallBudget,
    *,
    max_retries: int = DEFAULT_MAX_RETRIES,
    initial_backoff: float = INITIAL_BACKOFF_SECONDS,
):
    """Invoke the LLM with transient-error retry, optional fallback, and budget enforcement."""

    primary, fallback, fallback_wrapper = _resolve_providers(llm)
    last_exc: Exception | None = None

    for attempt in range(max_retries + 1):
        budget.consume()
        try:
            return primary.invoke(messages)
        except Exception as exc:  # noqa: BLE001 — classify transient provider errors
            last_exc = exc
            if fallback is not None and (
                is_quota_exhausted_error(exc) or is_connection_error(exc)
            ):
                return _invoke_fallback(fallback_wrapper, fallback, messages, budget, exc)
            if not is_transient_error(exc) or attempt >= max_retries:
                if fallback is not None and attempt >= max_retries:
                    return _invoke_fallback(fallback_wrapper, fallback, messages, budget, exc)
                raise
            time.sleep(initial_backoff * (2**attempt))

    if last_exc:
        raise last_exc
    raise RuntimeError("invoke_with_retry failed without exception")  # pragma: no cover


def _invoke_fallback(
    wrapper: FallbackChatModel | None,
    fallback: BaseChatModel,
    messages: list[BaseMessage],
    budget: CallBudget,
    primary_error: Exception,
):
    budget.consume()
    if wrapper is not None:
        wrapper.record_fallback_use(error=primary_error)
    try:
        return fallback.invoke(messages)
    except Exception as fallback_exc:
        if is_quota_exhausted_error(primary_error):
            raise primary_error from fallback_exc
        raise fallback_exc from primary_error


def _resolve_providers(
    llm: BaseChatModel | FallbackChatModel,
) -> tuple[BaseChatModel, BaseChatModel | None, FallbackChatModel | None]:
    if isinstance(llm, FallbackChatModel):
        return llm.primary, llm.fallback, llm
    return llm, None, None


def _normalize_provider(provider: str) -> str:
    normalized = (provider or "gemini").strip().lower()
    if normalized not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported LLM provider {provider!r}. "
            f"Expected one of: {', '.join(sorted(SUPPORTED_PROVIDERS))}."
        )
    return normalized


def is_transient_error(exc: Exception) -> bool:
    if is_quota_exhausted_error(exc):
        return False
    if is_connection_error(exc):
        return True
    message = str(exc).lower()
    markers = (
        "429",
        "rate limit",
        "503",
        "500",
        "502",
        "504",
        "overloaded",
        "unavailable",
    )
    return any(marker in message for marker in markers)


_CONNECTION_ERROR_TYPE_MARKERS = (
    "connectionerror",
    "connecterror",
    "connecttimeout",
    "readtimeout",
    "timeout",
)
_CONNECTION_ERROR_MESSAGE_MARKERS = (
    "connection refused",
    "all connection attempts failed",
    "name or service not known",
    "timed out",
    "connection reset",
    "unreachable",
    "failed to establish a new connection",
    "errno -2",
    "errno 111",
)


def is_connection_error(exc: Exception) -> bool:
    """Detect connection-level provider outages (refused, DNS, timeout, unreachable)."""

    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, (ConnectionError, TimeoutError)):
            return True
        type_name = type(current).__name__.lower()
        if any(marker in type_name for marker in _CONNECTION_ERROR_TYPE_MARKERS):
            return True
        message = str(current).lower()
        if any(marker in message for marker in _CONNECTION_ERROR_MESSAGE_MARKERS):
            return True
        current = current.__cause__ or current.__context__
    return False


def is_quota_exhausted_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(
        marker in message
        for marker in (
            "resource_exhausted",
            "quota exceeded",
            "exceeded your current quota",
            "generate_content_free_tier_requests",
        )
    )


def is_llm_credentials_error(exc: Exception) -> bool:
    message = str(exc).lower()
    type_name = type(exc).__name__.lower()
    return type_name == "authenticationerror" or any(
        marker in message
        for marker in (
            "401",
            "403",
            "missing authentication",
            "invalid api key",
            "incorrect api key",
            "unauthorized",
        )
    )


def is_llm_unavailable_error(exc: Exception) -> bool:
    return is_quota_exhausted_error(exc) or is_llm_credentials_error(exc)


def quota_exhausted_message(
    *,
    model: str | None = None,
    provider: str | None = None,
    fallback_provider: str | None = None,
) -> str:
    model_hint = f" ({model})" if model else ""
    provider_label = provider or "gemini"
    base = (
        f"The {provider_label} API quota is exhausted{model_hint}. "
        "Wait for the daily reset, switch models/providers, or use a billed API key."
    )
    if fallback_provider:
        base += f" A fallback provider ({fallback_provider}) is configured but also failed or was unavailable."
    else:
        base += (
            " To enable automatic fallback, set RETAIL_AGENT_FALLBACK_PROVIDER to "
            "openrouter or ollama and configure the matching credentials."
        )
    return base + " Report commands such as /save and show my reports still work without LLM calls."


def resolve_provider_model(settings: Settings, provider: str) -> str:
    """Return the configured model id for a provider name."""

    normalized = _normalize_provider(provider)
    if normalized == "gemini":
        return settings.model
    if normalized == "openrouter":
        return settings.openrouter_model
    if normalized == "ollama":
        return settings.ollama_model
    return settings.model


def format_llm_startup_line(settings: Settings) -> str:
    """Human-readable primary (and optional fallback) LLM for CLI startup."""

    primary = _normalize_provider(settings.provider)
    line = f"LLM: {primary} / {resolve_provider_model(settings, primary)}"
    if settings.fallback_provider:
        fallback = _normalize_provider(settings.fallback_provider)
        line += f" (fallback: {fallback} / {resolve_provider_model(settings, fallback)})"
    return line


def get_fallback_metadata(llm: BaseChatModel | FallbackChatModel) -> dict[str, object]:
    if not isinstance(llm, FallbackChatModel):
        return {}
    return {
        "primary_provider": llm.primary_provider,
        "fallback_provider": llm.fallback_provider,
        "fallback_count": llm.fallback_count,
        "last_fallback_provider": llm.last_fallback_provider,
        "last_primary_error": llm.last_primary_error,
    }
