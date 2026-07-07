"""Tests for LLM budget, provider factory, and fallback helpers."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from retail_agent.llm import (
    BudgetExhaustedError,
    CallBudget,
    FallbackChatModel,
    create_chat_model,
    get_fallback_metadata,
    invoke_with_retry,
    is_quota_exhausted_error,
    is_transient_error,
    quota_exhausted_message,
)
from tests.helpers import make_settings


class _FakeLLM:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def invoke(self, messages):
        outcome = self.outcomes[min(self.calls, len(self.outcomes) - 1)]
        self.calls += 1
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def test_call_budget_blocks_over_limit():
    budget = CallBudget(max_calls=2)
    budget.consume()
    budget.consume()
    with pytest.raises(BudgetExhaustedError):
        budget.consume()


def test_invoke_with_retry_retries_transient_errors():
    budget = CallBudget(max_calls=3)
    llm = _FakeLLM([RuntimeError("503 service unavailable"), HumanMessage(content="ok")])

    result = invoke_with_retry(llm, [HumanMessage(content="hi")], budget, initial_backoff=0)

    assert result.content == "ok"
    assert llm.calls == 2
    assert budget.used == 2


def test_invoke_with_retry_does_not_retry_non_transient_errors():
    budget = CallBudget(max_calls=3)
    llm = _FakeLLM([ValueError("bad prompt")])

    with pytest.raises(ValueError):
        invoke_with_retry(llm, [HumanMessage(content="hi")], budget)

    assert llm.calls == 1


def test_is_transient_error_detects_rate_limits():
    assert is_transient_error(RuntimeError("HTTP 429 Too Many Requests"))
    assert not is_transient_error(ValueError("invalid sql"))


def test_is_transient_error_does_not_retry_quota_exhausted():
    exc = RuntimeError(
        "429 RESOURCE_EXHAUSTED quota exceeded for "
        "generativelanguage.googleapis.com/generate_content_free_tier_requests"
    )
    assert is_quota_exhausted_error(exc)
    assert not is_transient_error(exc)


def test_normalize_provider_rejects_unknown_name():
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        create_chat_model(make_settings(provider="unknown"))


def test_gemini_provider_requires_google_api_key():
    with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
        create_chat_model(make_settings(provider="gemini", google_api_key=None))


def test_openrouter_provider_requires_openrouter_key():
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        create_chat_model(
            make_settings(
                provider="openrouter",
                google_api_key=None,
                openrouter_api_key=None,
            )
        )


def test_create_openrouter_model_without_gemini_key(monkeypatch):
    captured = {}

    class _FakeOpenAI:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr("langchain_openai.ChatOpenAI", _FakeOpenAI)

    create_chat_model(
        make_settings(
            provider="openrouter",
            google_api_key=None,
            openrouter_api_key="or-key",
            openrouter_model="test/model",
        )
    )

    assert captured["api_key"] == "or-key"
    assert captured["model"] == "test/model"
    assert captured["base_url"] == "https://openrouter.ai/api/v1"


def test_create_ollama_model(monkeypatch):
    captured = {}

    class _FakeOllama:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr("langchain_ollama.ChatOllama", _FakeOllama)

    create_chat_model(
        make_settings(
            provider="ollama",
            google_api_key=None,
            ollama_host="http://127.0.0.1:11434",
            ollama_model="llama3.2",
        )
    )

    assert captured["base_url"] == "http://127.0.0.1:11434"
    assert captured["model"] == "llama3.2"


def test_fallback_triggers_on_quota_exhausted(monkeypatch):
    monkeypatch.setattr("langchain_google_genai.ChatGoogleGenerativeAI", lambda **kwargs: object())
    monkeypatch.setattr("langchain_openai.ChatOpenAI", lambda **kwargs: object())

    settings = make_settings(
        provider="gemini",
        fallback_provider="openrouter",
        openrouter_api_key="or-key",
    )
    llm = create_chat_model(settings)
    assert isinstance(llm, FallbackChatModel)

    quota_error = RuntimeError(
        "429 RESOURCE_EXHAUSTED quota exceeded for generate_content_free_tier_requests"
    )
    llm.primary = _FakeLLM([quota_error])
    llm.fallback = _FakeLLM([AIMessage(content="fallback ok")])

    result = invoke_with_retry(llm, [HumanMessage(content="hi")], CallBudget(max_calls=3))

    assert result.content == "fallback ok"
    assert llm.fallback_count == 1
    assert llm.last_fallback_provider == "openrouter"
    metadata = get_fallback_metadata(llm)
    assert metadata["fallback_count"] == 1


def test_no_fallback_preserves_primary_error():
    llm = _FakeLLM(
        [
            RuntimeError(
                "429 RESOURCE_EXHAUSTED quota exceeded for generate_content_free_tier_requests"
            )
        ]
    )

    with pytest.raises(RuntimeError):
        invoke_with_retry(llm, [HumanMessage(content="hi")], CallBudget(max_calls=1))


def test_budget_exhaustion_blocks_fallback():
    llm = FallbackChatModel(
        primary=_FakeLLM(
            [
                RuntimeError(
                    "429 RESOURCE_EXHAUSTED quota exceeded for generate_content_free_tier_requests"
                )
            ]
        ),
        fallback=_FakeLLM([AIMessage(content="fallback ok")]),
        primary_provider="gemini",
        fallback_provider="openrouter",
    )

    with pytest.raises(BudgetExhaustedError):
        invoke_with_retry(llm, [HumanMessage(content="hi")], CallBudget(max_calls=1))

    assert llm.fallback_count == 0


def test_quota_message_mentions_fallback_when_configured():
    message = quota_exhausted_message(
        model="gemini-2.5-flash",
        provider="gemini",
        fallback_provider="openrouter",
    )
    assert "openrouter" in message


def test_quota_message_explains_how_to_enable_fallback():
    message = quota_exhausted_message(provider="gemini")
    assert "RETAIL_AGENT_FALLBACK_PROVIDER" in message
