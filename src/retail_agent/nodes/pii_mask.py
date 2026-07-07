"""Mask PII in query results before report composition."""

from __future__ import annotations

import logging

import pandas as pd

from retail_agent.deps import AgentDeps
from retail_agent.preview import dataframe_preview
from retail_agent.safety import mask_dataframe
from retail_agent.state import AgentState

logger = logging.getLogger(__name__)


def pii_mask(state: AgentState, deps: AgentDeps) -> dict:
    rows = state.get("result_rows") or []
    if not rows:
        return {}

    df = pd.DataFrame(rows)
    masked = mask_dataframe(df)
    note_required = bool(state.get("pii_note_required")) or masked.pii_note_required

    logger.info(
        "Masked PII columns=%s hits=%s",
        list(masked.masked_columns),
        masked.mask_hit_count,
    )

    return {
        "result_preview": dataframe_preview(masked.dataframe),
        "pii_masked": bool(masked.masked_columns),
        "pii_mask_hits": masked.mask_hit_count,
        "pii_masked_columns": list(masked.masked_columns),
        "pii_note_required": note_required,
        "result_rows": None,
    }
