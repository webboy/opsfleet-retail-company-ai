"""Compose an analyst-style report from query results."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from retail_agent.deps import AgentDeps
from retail_agent.llm import BudgetExhaustedError, CallBudget, invoke_with_retry
from retail_agent.personas import load_persona
from retail_agent.state import AgentState
from retail_agent.stores import output_format_instruction


def compose_report(state: AgentState, deps: AgentDeps) -> dict:
    budget = CallBudget.from_dict(state.get("llm_budget"))
    question = state.get("question") or ""
    sql = state.get("sql") or ""
    preview = state.get("result_preview") or ""
    conversation = _conversation_snippet(state)
    user_id = state.get("user_id") or ""
    prefs = deps.report_store.get_preferences(user_id)
    persona_name = state.get("persona_name") or deps.settings.persona
    persona_text = _load_persona_text(persona_name, deps)
    format_instruction = output_format_instruction(
        prefs.output_format if prefs else None
    )

    system_prompt = (
        f"{persona_text}\n\n"
        "Write a concise, clear answer grounded in the SQL results. "
        "Do not mention SQL errors or internal retries. "
        "Never include raw customer emails or phone numbers in the report. "
        "The result sample may already contain masked contact details. "
        f"{format_instruction}"
    )

    try:
        response = invoke_with_retry(
            deps.llm,
            [
                SystemMessage(content=system_prompt),
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


def _load_persona_text(persona_name: str, deps: AgentDeps) -> str:
    try:
        return load_persona(
            persona_name,
            personas_dir=deps.settings.personas_dir,
        )
    except (FileNotFoundError, ValueError):
        return load_persona("default", personas_dir=deps.settings.personas_dir)


def _conversation_snippet(state: AgentState, *, limit: int = 6) -> str:
    messages = state.get("messages") or []
    lines: list[str] = []
    for message in messages[-limit:]:
        role = getattr(message, "type", "message")
        lines.append(f"{role}: {message.content}")
    return "\n".join(lines) if lines else "(no prior conversation)"
