"""Capture successful turns as candidate trios for analyst review."""

from __future__ import annotations

import logging

from retail_agent.deps import AgentDeps
from retail_agent.state import AgentState

logger = logging.getLogger(__name__)


def capture_candidate(state: AgentState, deps: AgentDeps) -> dict:
    if state.get("status") != "done":
        return {}

    question = state.get("question") or ""
    sql = state.get("sql") or ""
    report = state.get("report") or ""
    if not question or not sql or not report:
        return {}

    path = deps.trio_store.capture_candidate(
        question=question,
        sql=sql,
        report=report,
        retrieved_trio_ids=state.get("retrieved_trio_ids") or [],
        user_id=state.get("user_id"),
    )
    logger.info("Captured candidate trio to %s", path)
    return {"candidate_captured": True}
