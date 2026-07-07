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


def is_greeting_or_chitchat(question: str) -> bool:
    q = question.lower().strip().rstrip("!?.,")
    if not q:
        return False
    exact = {
        "hello",
        "helo",
        "hi",
        "hey",
        "thanks",
        "thank you",
        "good morning",
        "good afternoon",
        "good evening",
    }
    if q in exact:
        return True
    words = q.split()
    if len(words) <= 4 and words[0] in {"hello", "helo", "hi", "hey"}:
        return True
    return False
