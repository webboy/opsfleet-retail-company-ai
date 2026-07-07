"""Friendly reply for greetings and other non-analytic chitchat."""

from __future__ import annotations

from langchain_core.messages import AIMessage

from retail_agent.state import AgentState


def answer_chitchat(state: AgentState) -> dict:
    report = (
        "Hello! I'm a retail data analysis assistant. You can ask me about sales, "
        "customers, product performance, revenue trends, or our database schema."
    )
    return {
        "report": report,
        "status": "done",
        "messages": [AIMessage(content=report)],
    }
