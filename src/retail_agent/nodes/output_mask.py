"""Sweep final report text for leaked PII."""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage

from retail_agent.deps import AgentDeps
from retail_agent.safety import append_pii_policy_note, mask_text
from retail_agent.state import AgentState

logger = logging.getLogger(__name__)


def output_mask(state: AgentState, deps: AgentDeps) -> dict:
    report = state.get("report") or ""
    masked_report, text_hits = mask_text(report)
    note_required = bool(state.get("pii_note_required")) or text_hits > 0
    final_report = append_pii_policy_note(masked_report, note_required=note_required)

    total_hits = int(state.get("pii_mask_hits") or 0) + text_hits
    if text_hits:
        logger.info("Output mask swept %s additional PII hits from report text", text_hits)

    updates: dict = {
        "report": final_report,
        "pii_note_required": note_required,
        "pii_mask_hits": total_hits,
        "messages": [AIMessage(content=final_report)],
    }
    if (
        state.get("report_complete")
        and state.get("status") == "done"
        and state.get("query_ok")
    ):
        updates.update(
            {
                "last_analysis_report": final_report,
                "last_analysis_question": state.get("question") or None,
                "last_analysis_sql": state.get("sql"),
                "last_analysis_complete": True,
            }
        )
    return updates
