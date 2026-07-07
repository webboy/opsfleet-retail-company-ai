"""SQL extraction helpers."""

from __future__ import annotations

import re


_SQL_BLOCK_RE = re.compile(r"```(?:sql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)


def extract_sql(text: str) -> str:
    """Extract SQL from a model response."""

    match = _SQL_BLOCK_RE.search(text)
    if match:
        return match.group(1).strip()
    return text.strip().strip("`").strip()


def is_schema_question(question: str) -> bool:
    q = question.lower()
    markers = (
        "what tables",
        "which tables",
        "what columns",
        "table structure",
        "database structure",
        "schema",
        "describe the database",
        "what data do you have",
    )
    return any(marker in q for marker in markers)
