"""SQLite persistence for saved reports."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

ReportSelectorKind = Literal["mention", "today", "all"]
OutputFormat = Literal["table", "bullets", "prose"]


@dataclass(frozen=True)
class ReportSelector:
    kind: ReportSelectorKind
    mention: str | None = None


@dataclass(frozen=True)
class UserPreferences:
    user_id: str
    output_format: OutputFormat | None
    notes: str | None
    updated_at: str | None = None


@dataclass(frozen=True)
class SavedReport:
    id: str
    owner: str
    title: str
    content: str
    question: str | None
    sql: str | None
    created_at: str
    tags: str | None = None


class ReportStore:
    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = Path(db_path or _default_db_path())
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def save_report(
        self,
        *,
        owner: str,
        title: str,
        content: str,
        question: str | None = None,
        sql: str | None = None,
        tags: str | None = None,
    ) -> SavedReport:
        report_id = uuid.uuid4().hex
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO reports (id, owner, title, content, question, sql, created_at, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (report_id, owner, title, content, question, sql, created_at, tags),
            )
            conn.commit()
        return SavedReport(
            id=report_id,
            owner=owner,
            title=title,
            content=content,
            question=question,
            sql=sql,
            created_at=created_at,
            tags=tags,
        )

    def list_reports(self, owner: str) -> list[SavedReport]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, owner, title, content, question, sql, created_at, tags
                FROM reports
                WHERE owner = ?
                ORDER BY created_at DESC
                """,
                (owner,),
            ).fetchall()
        return [_row_to_report(row) for row in rows]

    def get_report(self, owner: str, report_id: str) -> SavedReport | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, owner, title, content, question, sql, created_at, tags
                FROM reports
                WHERE owner = ? AND id = ?
                """,
                (owner, report_id),
            ).fetchone()
        return _row_to_report(row) if row else None

    def find_reports(self, owner: str, selector: ReportSelector) -> list[SavedReport]:
        reports = self.list_reports(owner)
        if selector.kind == "all":
            return reports
        if selector.kind == "today":
            today = datetime.now(timezone.utc).date().isoformat()
            return [report for report in reports if report.created_at[:10] == today]
        if selector.kind == "mention" and selector.mention:
            needle = selector.mention.lower()
            return [
                report
                for report in reports
                if needle in report.title.lower()
                or needle in report.content.lower()
                or needle in (report.question or "").lower()
                or needle in (report.tags or "").lower()
            ]
        return []

    def delete_reports(self, owner: str, report_ids: list[str]) -> int:
        if not report_ids:
            return 0
        placeholders = ",".join("?" for _ in report_ids)
        params = [owner, *report_ids]
        with self._connect() as conn:
            cursor = conn.execute(
                f"DELETE FROM reports WHERE owner = ? AND id IN ({placeholders})",
                params,
            )
            conn.commit()
            return int(cursor.rowcount)

    def get_preferences(self, user_id: str) -> UserPreferences | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT user_id, output_format, notes, updated_at
                FROM preferences
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
        return _row_to_preferences(row) if row else None

    def set_output_format(
        self,
        user_id: str,
        output_format: OutputFormat,
        *,
        notes: str | None = None,
    ) -> UserPreferences:
        updated_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO preferences (user_id, output_format, notes, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    output_format = excluded.output_format,
                    notes = COALESCE(excluded.notes, preferences.notes),
                    updated_at = excluded.updated_at
                """,
                (user_id, output_format, notes, updated_at),
            )
            conn.commit()
        return UserPreferences(
            user_id=user_id,
            output_format=output_format,
            notes=notes,
            updated_at=updated_at,
        )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    id TEXT PRIMARY KEY,
                    owner TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    question TEXT,
                    sql TEXT,
                    created_at TEXT NOT NULL,
                    tags TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_reports_owner ON reports(owner)"
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS preferences (
                    user_id TEXT PRIMARY KEY,
                    output_format TEXT,
                    notes TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.commit()


def format_report_summary(report: SavedReport) -> str:
    created = report.created_at[:10]
    return f"- {report.title} ({created})"


def format_candidate_list(reports: list[SavedReport]) -> str:
    lines = [format_report_summary(report) for report in reports]
    return "\n".join(lines)


def format_preferences_summary(prefs: UserPreferences | None) -> str:
    if prefs is None or prefs.output_format is None:
        return "You have no saved output preferences yet."
    lines = [f"Output format: {prefs.output_format}"]
    if prefs.notes:
        lines.append(f"Notes: {prefs.notes}")
    if prefs.updated_at:
        lines.append(f"Updated: {prefs.updated_at[:10]}")
    return "\n".join(lines)


def output_format_instruction(output_format: OutputFormat | None) -> str:
    if output_format == "table":
        return "Format the answer primarily as a markdown table when the data supports it."
    if output_format == "bullets":
        return "Format the answer as concise bullet points."
    if output_format == "prose":
        return "Format the answer as short prose paragraphs without bullet lists."
    return "Use short paragraphs or bullet points when helpful."


def is_delete_confirmed(reply: object) -> bool:
    if reply is None:
        return False
    if isinstance(reply, dict):
        reply = reply.get("confirmation") or reply.get("value") or ""
    normalized = str(reply).strip().lower()
    return normalized in {"yes", "y", "confirm", "delete"}


def _row_to_report(row: sqlite3.Row) -> SavedReport:
    return SavedReport(
        id=row["id"],
        owner=row["owner"],
        title=row["title"],
        content=row["content"],
        question=row["question"],
        sql=row["sql"],
        created_at=row["created_at"],
        tags=row["tags"],
    )


def _row_to_preferences(row: sqlite3.Row) -> UserPreferences:
    output_format = row["output_format"]
    return UserPreferences(
        user_id=row["user_id"],
        output_format=output_format if output_format else None,  # type: ignore[arg-type]
        notes=row["notes"],
        updated_at=row["updated_at"],
    )


def _default_db_path() -> Path:
    from os import getenv

    configured = getenv("RETAIL_AGENT_DB_PATH")
    if configured:
        return Path(configured)
    return Path.cwd() / "data" / "reports.sqlite3"
