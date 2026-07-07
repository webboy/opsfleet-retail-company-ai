"""Compose an analyst-style report from query results."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from retail_agent.deps import AgentDeps
from retail_agent.llm import BudgetExhaustedError, CallBudget, invoke_with_retry
from retail_agent.state import AgentState


def compose_report(state: AgentState, deps: AgentDeps) -> dict:
    budget = CallBudget.from_dict(state.get("llm_budget"))
    question = state.get("question") or ""
    sql = state.get("sql") or ""
    preview = state.get("result_preview") or ""
    conversation = _conversation_snippet(state)

    try:
        response = invoke_with_retry(
            deps.llm,
            [
                SystemMessage(
                    content=(
                        "You are a retail data analyst writing for a non-technical executive. "
                        "Write a concise, clear answer grounded in the SQL results. "
                        "Do not mention SQL errors or internal retries. "
                        "Never include raw customer emails or phone numbers in the report. "
                        "The result sample may already contain masked contact details. "
                        "Use short paragraphs or bullet points when helpful."
                    )
                ),
                HumanMessage(
                    content=(
                        f"Conversation:\n{conversation}\n\n"
                        f"Question: {question}\n\n"
                        f"SQL used:\n{sql}\n\n"
                        f"Result sample:\n{preview}\n\n"
                        "Write the analyst report."
                    )
                ),
            ],
            budget,
        )
        report = str(response.content).strip()
    except BudgetExhaustedError:
        report = (
            "I retrieved the data but couldn't finish composing the report within the "
            "LLM call limit for this turn. Please try a simpler question."
        )

    return {
        "report": report,
        "status": "done",
        "llm_budget": budget.to_dict(),
    }


def _conversation_snippet(state: AgentState, *, limit: int = 6) -> str:
    messages = state.get("messages") or []
    lines: list[str] = []
    for message in messages[-limit:]:
        role = getattr(message, "type", "message")
        lines.append(f"{role}: {message.content}")
    return "\n".join(lines) if lines else "(no prior conversation)"
