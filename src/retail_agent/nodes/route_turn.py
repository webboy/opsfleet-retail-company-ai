"""Route a turn to schema or analysis handling."""

from __future__ import annotations

from retail_agent.deps import AgentDeps, resolve_budget
from retail_agent.llm import CallBudget
from retail_agent.sql_utils import is_greeting_or_chitchat, is_schema_question
from retail_agent.state import AgentState


def route_turn(state: AgentState, deps: AgentDeps) -> dict:
    question = state.get("question") or _latest_user_message(state)
    guard_route = state.get("guard_route")
    if guard_route == "chitchat":
        turn_mode = "chitchat"
    elif guard_route == "schema":
        turn_mode = "schema"
    elif guard_route == "analysis":
        turn_mode = "analysis"
    elif is_greeting_or_chitchat(question):
        turn_mode = "chitchat"
    elif is_schema_question(question):
        turn_mode = "schema"
    else:
        turn_mode = "analysis"

    budget = resolve_budget(state, deps)
    return {
        "question": question,
        "turn_mode": turn_mode,
        "sql_attempts": 0,
        "max_sql_attempts": deps.max_sql_attempts,
        "llm_budget": budget.to_dict(),
        "status": "running",
        "last_error": None,
        "query_ok": False,
        "query_empty": False,
        "report": None,
        "result_rows": None,
        "pii_masked": False,
        "pii_mask_hits": 0,
        "pii_masked_columns": [],
    }


def _latest_user_message(state: AgentState) -> str:
    messages = state.get("messages") or []
    for message in reversed(messages):
        if getattr(message, "type", "") == "human":
            return str(message.content)
    return ""
