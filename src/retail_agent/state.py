"""LangGraph agent state definition."""

from __future__ import annotations

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str
    question: str
    turn_mode: Literal["analysis", "schema"]
    sql: str | None
    sql_attempts: int
    max_sql_attempts: int
    last_error: str | None
    query_ok: bool
    query_empty: bool
    result_preview: str | None
    report: str | None
    llm_budget: dict[str, int]
    status: Literal["running", "done", "fallback"]
