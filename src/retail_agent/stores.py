"""SQLite persistence for saved reports."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

ReportSelectorKind = Literal["mention", "today", "all"]


@dataclass(frozen=True)
class ReportSelector:
    kind: ReportSelectorKind
    mention: str | None = None


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
            conn.commit()


def format_report_summary(report: SavedReport) -> str:
    created = report.created_at[:10]
    return f"- {report.title} ({created})"


def format_candidate_list(reports: list[SavedReport]) -> str:
    lines = [format_report_summary(report) for report in reports]
    return "\n".join(lines)


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


def _default_db_path() -> Path:
    from os import getenv

    configured = getenv("RETAIL_AGENT_DB_PATH")
    if configured:
        return Path(configured)
    return Path.cwd() / "data" / "reports.sqlite3"
