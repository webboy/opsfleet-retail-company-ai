"""Deterministic input guard helpers and PII masking."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

import pandas as pd

from retail_agent.sql_utils import is_greeting_or_chitchat, is_schema_question
from retail_agent.stores import OutputFormat

GuardRoute = Literal["analysis", "schema", "chitchat", "off_topic", "malicious", "reports", "preferences"]
GuardDecision = Literal["allowed", "refused"]
ReportAction = Literal["save", "list", "delete"]
PreferenceAction = Literal["set", "show"]

EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\d)"
)

PII_COLUMN_MARKERS = (
    "email",
    "e_mail",
    "phone",
    "mobile",
    "cell",
    "telephone",
    "contact",
    "fax",
)

ANALYSIS_MARKERS = (
    "revenue",
    "sales",
    "order",
    "customer",
    "product",
    "spend",
    "buyer",
    "category",
    "department",
    "traffic",
    "cancel",
    "return",
    "monthly",
    "month",
    "weekly",
    "daily",
    "day",
    "days",
    "last",
    "week",
    "give me",
    "show me",
    "how many",
    "how much",
    "total",
    "number",
    "sale",
    "top",
    "average",
    "count",
    "performance",
    "inventory",
    "branch",
    "store",
)

OFF_TOPIC_MARKERS = (
    "write me a poem",
    "write a poem",
    "tell me a joke",
    "joke",
    "weather",
    "recipe",
    "translate this",
    "who won the",
    "capital of",
    "write code for",
    "python script for",
)

MALICIOUS_MARKERS = (
    "ignore previous instructions",
    "ignore your instructions",
    "ignore all instructions",
    "disregard previous instructions",
    "dump users table",
    "dump the users",
    "drop table",
    "delete from",
    "truncate table",
    "system prompt",
    "reveal your instructions",
    "bypass safety",
)

PII_REQUEST_MARKERS = (
    "email",
    "emails",
    "phone",
    "phones",
    "contact details",
    "contact info",
)

REPORT_LIST_MARKERS = (
    "show my reports",
    "list my reports",
    "my saved reports",
    "show saved reports",
)

REPORT_SAVE_MARKERS = (
    "/save",
    "save this report",
    "save the report",
    "save report",
)

_MENTION_DELETE_PATTERNS = (
    re.compile(r"delete(?:\s+all)?\s+reports?\s+mentioning\s+(.+)", re.IGNORECASE),
    re.compile(r"delete\s+reports?\s+about\s+(.+)", re.IGNORECASE),
)

PREFERENCE_SHOW_MARKERS = (
    "/prefs",
    "show my preferences",
    "my preferences",
    "what are my preferences",
)

_TABLE_PREFERENCE_PATTERNS = (
    re.compile(r"\b(?:i prefer|prefer|use)\b.*\btables?\b", re.IGNORECASE),
    re.compile(r"\btable format\b", re.IGNORECASE),
    re.compile(r"\bformat.*\btables?\b", re.IGNORECASE),
)

_BULLET_PREFERENCE_PATTERNS = (
    re.compile(r"\b(?:i prefer|prefer|use)\b.*\bbullet points?\b", re.IGNORECASE),
    re.compile(r"\bbullet points?\b.*\bfrom now on\b", re.IGNORECASE),
    re.compile(r"\bgive me bullet points\b", re.IGNORECASE),
)

_PROSE_PREFERENCE_PATTERNS = (
    re.compile(r"\b(?:i prefer|prefer|use)\b.*\b(?:prose|paragraphs?)\b", re.IGNORECASE),
    re.compile(r"\b(?:prose|paragraphs?)\b.*\bfrom now on\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class PreferenceCommand:
    action: PreferenceAction
    output_format: OutputFormat | None = None
    notes: str | None = None


@dataclass(frozen=True)
class ReportCommand:
    action: ReportAction
    selector_kind: Literal["mention", "today", "all"] | None = None
    mention: str | None = None


@dataclass(frozen=True)
class InputPrecheck:
    decision: GuardDecision
    route: GuardRoute
    reason: str
    needs_llm: bool = False
    pii_sensitive: bool = False


@dataclass(frozen=True)
class MaskDataframeResult:
    dataframe: pd.DataFrame
    masked_columns: tuple[str, ...]
    mask_hit_count: int
    pii_note_required: bool


PII_POLICY_NOTE = (
    "Note: Customer contact details such as emails and phone numbers are masked "
    "for privacy."
)


def classify_input_precheck(question: str) -> InputPrecheck:
    text = (question or "").strip()
    lowered = text.lower()

    if not text:
        return InputPrecheck(
            decision="refused",
            route="off_topic",
            reason="empty question",
        )

    if is_greeting_or_chitchat(text):
        return InputPrecheck(
            decision="allowed",
            route="chitchat",
            reason="greeting or chitchat",
        )

    if is_schema_question(text):
        return InputPrecheck(
            decision="allowed",
            route="schema",
            reason="schema question",
        )

    if parse_report_command(text):
        return InputPrecheck(
            decision="allowed",
            route="reports",
            reason="report management",
        )

    if parse_preference_command(text):
        return InputPrecheck(
            decision="allowed",
            route="preferences",
            reason="preference management",
        )

    if any(marker in lowered for marker in MALICIOUS_MARKERS):
        return InputPrecheck(
            decision="refused",
            route="malicious",
            reason="prompt injection or destructive request",
        )

    if any(marker in lowered for marker in OFF_TOPIC_MARKERS):
        return InputPrecheck(
            decision="refused",
            route="off_topic",
            reason="off-topic request",
        )

    pii_sensitive = any(marker in lowered for marker in PII_REQUEST_MARKERS)
    if any(marker in lowered for marker in ANALYSIS_MARKERS):
        return InputPrecheck(
            decision="allowed",
            route="analysis",
            reason="retail analysis question",
            pii_sensitive=pii_sensitive,
        )

    return InputPrecheck(
        decision="allowed",
        route="analysis",
        reason="ambiguous retail question",
        needs_llm=True,
        pii_sensitive=pii_sensitive,
    )


def parse_report_command(question: str) -> ReportCommand | None:
    text = (question or "").strip()
    lowered = text.lower()

    if lowered in REPORT_SAVE_MARKERS:
        return ReportCommand(action="save")

    if any(marker in lowered for marker in REPORT_LIST_MARKERS):
        return ReportCommand(action="list")

    if "delete" not in lowered or "report" not in lowered:
        return None

    if "today" in lowered or "we made today" in lowered:
        return ReportCommand(action="delete", selector_kind="today")

    if "all my reports" in lowered or lowered.strip() == "delete my reports":
        return ReportCommand(action="delete", selector_kind="all")

    for pattern in _MENTION_DELETE_PATTERNS:
        match = pattern.search(text)
        if match:
            mention = match.group(1).strip().strip("\"'")
            if mention:
                return ReportCommand(action="delete", selector_kind="mention", mention=mention)

    return None


def parse_preference_command(question: str) -> PreferenceCommand | None:
    text = (question or "").strip()
    lowered = text.lower()

    if lowered in PREFERENCE_SHOW_MARKERS:
        return PreferenceCommand(action="show")

    for pattern in _TABLE_PREFERENCE_PATTERNS:
        if pattern.search(text):
            return PreferenceCommand(action="set", output_format="table")

    for pattern in _BULLET_PREFERENCE_PATTERNS:
        if pattern.search(text):
            return PreferenceCommand(action="set", output_format="bullets")

    for pattern in _PROSE_PREFERENCE_PATTERNS:
        if pattern.search(text):
            return PreferenceCommand(action="set", output_format="prose")

    return None


def parse_llm_guard_label(text: str) -> GuardRoute:
    normalized = text.strip().lower()
    for label in ("malicious", "off_topic", "analysis", "schema", "chitchat"):
        if label in normalized:
            return label  # type: ignore[return-value]
    if "refuse" in normalized or "decline" in normalized:
        return "off_topic"
    return "analysis"


def refusal_message(route: GuardRoute) -> str:
    if route == "malicious":
        return (
            "I can't help with that request. I'm a retail data analysis assistant "
            "and can only answer questions about sales, products, customers, and "
            "the database schema using read-only analytics."
        )
    return (
        "I'm focused on retail sales, product, and customer analytics. "
        "Please ask a business or data question, or type /help for examples."
    )


def mask_dataframe(df: pd.DataFrame) -> MaskDataframeResult:
    if df.empty:
        return MaskDataframeResult(
            dataframe=df.copy(),
            masked_columns=(),
            mask_hit_count=0,
            pii_note_required=False,
        )

    masked = df.copy()
    masked_columns: list[str] = []
    mask_hits = 0

    for column in masked.columns:
        series = masked[column]
        if _column_is_pii(column) or _series_contains_pii(series):
            masked_columns.append(str(column))
            masked[column] = series.map(_mask_cell_value)
            mask_hits += int(series.notna().sum())

    return MaskDataframeResult(
        dataframe=masked,
        masked_columns=tuple(masked_columns),
        mask_hit_count=mask_hits,
        pii_note_required=bool(masked_columns),
    )


def mask_text(text: str) -> tuple[str, int]:
    hits = 0

    def _mask_email(match: re.Match[str]) -> str:
        nonlocal hits
        hits += 1
        return _mask_email_value(match.group(0))

    def _mask_phone(match: re.Match[str]) -> str:
        nonlocal hits
        hits += 1
        return _mask_phone_value(match.group(0))

    masked = EMAIL_RE.sub(_mask_email, text)
    masked = PHONE_RE.sub(_mask_phone, masked)
    return masked, hits


def append_pii_policy_note(report: str, *, note_required: bool) -> str:
    if not note_required:
        return report
    if PII_POLICY_NOTE.lower() in report.lower():
        return report
    return f"{report.rstrip()}\n\n{PII_POLICY_NOTE}"


def _column_is_pii(column: object) -> bool:
    name = str(column).lower()
    return any(marker in name for marker in PII_COLUMN_MARKERS)


def _series_contains_pii(series: pd.Series, *, sample_size: int = 25) -> bool:
    sample = series.dropna().astype(str).head(sample_size)
    for value in sample:
        if EMAIL_RE.search(value) or PHONE_RE.search(value):
            return True
    return False


def _mask_cell_value(value: object) -> object:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return value
    text = str(value)
    if EMAIL_RE.fullmatch(text) or EMAIL_RE.search(text):
        return _mask_email_value(text)
    if PHONE_RE.fullmatch(text) or PHONE_RE.search(text):
        return _mask_phone_value(text)
    if _column_is_pii(text):
        return "***"
    return text


def _mask_email_value(email: str) -> str:
    match = EMAIL_RE.search(email)
    if not match:
        return "***@***.***"
    local = match.group(0).split("@", 1)[0]
    prefix = local[:1] if local else "*"
    return f"{prefix}***@***.***"


def _mask_phone_value(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    suffix = digits[-4:] if len(digits) >= 4 else "****"
    return f"***-***-{suffix}"
