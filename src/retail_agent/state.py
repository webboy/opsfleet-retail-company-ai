"""LangGraph agent state definition."""

from __future__ import annotations

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str
    question: str
    turn_mode: Literal["analysis", "schema", "chitchat"]
    guard_decision: Literal["allowed", "refused"]
    guard_route: str
    guard_reason: str | None
    pii_masked: bool
    pii_mask_hits: int
    pii_masked_columns: list[str]
    pii_note_required: bool
    result_rows: list[dict] | None
    retrieved_trios: list[dict]
    retrieved_trio_ids: list[str]
    retrieval_method: str
    candidate_captured: bool
    sql: str | None
    sql_attempts: int
    max_sql_attempts: int
    last_error: str | None
    query_ok: bool
    query_empty: bool
    result_preview: str | None
    report: str | None
    last_analysis_report: str | None
    last_analysis_question: str | None
    last_analysis_sql: str | None
    report_action: Literal["save", "list", "delete"] | None
    report_selector_kind: Literal["mention", "today", "all"] | None
    report_mention: str | None
    pending_delete_report_ids: list[str] | None
    pending_delete_summary: str | None
    preference_action: Literal["set", "show"] | None
    preference_output_format: Literal["table", "bullets", "prose"] | None
    persona_name: str | None
    llm_budget: dict[str, int]
    status: Literal["running", "done", "fallback"]
