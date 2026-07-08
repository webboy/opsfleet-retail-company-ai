"""Answer database-structure questions from static schema docs."""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from retail_agent.deps import AgentDeps
from retail_agent.llm import (
    BudgetExhaustedError,
    CallBudget,
    invoke_with_retry,
    is_llm_unavailable_error,
    is_quota_exhausted_error,
    quota_exhausted_message,
)
from retail_agent.schema_doc import load_schema_doc
from retail_agent.state import AgentState


def answer_schema(state: AgentState, deps: AgentDeps) -> dict:
    budget = CallBudget.from_dict(state.get("llm_budget"))
    question = state.get("question") or ""

    try:
        response = invoke_with_retry(
            deps.llm,
            [
                SystemMessage(
                    content=(
                        "You are a retail data analyst assistant. Answer questions about "
                        "the database schema clearly for a non-technical executive. "
                        "Use only the schema documentation provided."
                    )
                ),
                HumanMessage(
                    content=(
                        f"Schema documentation:\n{load_schema_doc()}\n\n"
                        f"User question: {question}"
                    )
                ),
            ],
            budget,
        )
        report = str(response.content).strip()
    except BudgetExhaustedError:
        report = (
            "I can describe the database using our schema documentation, but I hit the "
            "LLM call limit for this turn. Please ask again with a narrower question."
        )
    except Exception as exc:
        if is_llm_unavailable_error(exc):
            if is_quota_exhausted_error(exc):
                report = quota_exhausted_message(
                    model=deps.settings.model,
                    provider=deps.settings.provider,
                    fallback_provider=deps.settings.fallback_provider,
                )
            else:
                report = str(exc) or "LLM authentication failed."
            return {
                "report": report,
                "status": "fallback",
                "llm_budget": budget.to_dict(),
                "messages": [AIMessage(content=report)],
            }
        raise

    return {
        "report": report,
        "status": "done",
        "llm_budget": budget.to_dict(),
        "messages": [AIMessage(content=report)],
    }
