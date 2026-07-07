"""LLM factory, retry/backoff, and per-turn call budget."""

from __future__ import annotations

import time
from dataclasses import dataclass

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from retail_agent.config import Settings, get_settings

DEFAULT_MAX_LLM_CALLS = 8
DEFAULT_MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1.0


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


def create_chat_model(settings: Settings | None = None) -> BaseChatModel:
    settings = settings or get_settings()
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is required for the chat agent.")
    return ChatGoogleGenerativeAI(
        model=settings.model,
        google_api_key=settings.google_api_key,
        temperature=0.1,
    )


def invoke_with_retry(
    llm: BaseChatModel,
    messages: list[BaseMessage],
    budget: CallBudget,
    *,
    max_retries: int = DEFAULT_MAX_RETRIES,
    initial_backoff: float = INITIAL_BACKOFF_SECONDS,
):
    """Invoke the LLM with transient-error retry and budget enforcement."""

    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        budget.consume()
        try:
            return llm.invoke(messages)
        except Exception as exc:  # noqa: BLE001 — classify transient provider errors
            last_exc = exc
            if not is_transient_error(exc) or attempt >= max_retries:
                raise
            time.sleep(initial_backoff * (2**attempt))
    if last_exc:
        raise last_exc
    raise RuntimeError("invoke_with_retry failed without exception")  # pragma: no cover


def is_transient_error(exc: Exception) -> bool:
    if is_quota_exhausted_error(exc):
        return False
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


def quota_exhausted_message(*, model: str | None = None) -> str:
    model_hint = f" ({model})" if model else ""
    return (
        "The Gemini API quota is exhausted{model_hint}. The free tier allows roughly "
        "20 requests per day per model. Wait for the daily reset, set a different "
        "RETAIL_AGENT_MODEL in .env, or use a billed API key. "
        "Report commands such as /save and show my reports still work without LLM calls."
    ).format(model_hint=model_hint)
