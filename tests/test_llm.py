"""Tests for LLM budget and retry helpers."""

import pytest
from langchain_core.messages import HumanMessage

from retail_agent.llm import (
    BudgetExhaustedError,
    CallBudget,
    invoke_with_retry,
    is_transient_error,
)


class _FakeLLM:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def invoke(self, messages):
        outcome = self.outcomes[self.calls]
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
    llm = _FakeLLM([RuntimeError("429 rate limit"), HumanMessage(content="ok")])

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
