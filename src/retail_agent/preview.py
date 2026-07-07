"""Format query results for LLM prompts."""

from __future__ import annotations

import pandas as pd


def dataframe_preview(df: pd.DataFrame, *, max_rows: int = 20) -> str:
    if df.empty:
        return "(empty result set)"
    preview = df.head(max_rows)
    text = preview.to_csv(index=False)
    if len(df) > max_rows:
        text += f"\n... ({len(df) - max_rows} more rows)"
    return text
