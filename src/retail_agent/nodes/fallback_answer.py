"""Graceful fallback when SQL self-heal is exhausted."""

from __future__ import annotations

from langchain_core.messages import AIMessage

from retail_agent.state import AgentState


def fallback_answer(state: AgentState) -> dict:
    if state.get("guard_decision") == "refused":
        report = state.get("report") or (
            "I'm focused on retail sales, product, and customer analytics."
        )
        return {
            "report": report,
            "status": "fallback",
            "messages": [AIMessage(content=report)],
        }

    question = state.get("question") or "your question"
    last_error = state.get("last_error")
    detail = ""
    if last_error and "budget" not in last_error.lower():
        detail = " I tried a few query variations but couldn't produce a reliable answer."

    report = (
        f"I'm sorry — I couldn't answer {question!r} with the available data.{detail} "
        "Could you rephrase the question, specify a date range, or narrow the scope?"
    )
    return {
        "report": report,
        "status": "fallback",
        "messages": [AIMessage(content=report)],
    }
