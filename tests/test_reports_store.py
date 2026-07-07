"""Unit tests for the SQLite report store."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from retail_agent.stores import ReportSelector, ReportStore, is_delete_confirmed


@pytest.fixture
def store(tmp_path):
    return ReportStore(db_path=tmp_path / "reports.sqlite3")


def test_save_and_list_reports(store):
    saved = store.save_report(
        owner="alice",
        title="Top orders",
        content="Report body",
        question="Show top orders",
        sql="SELECT 1",
    )

    reports = store.list_reports("alice")
    assert len(reports) == 1
    assert reports[0].id == saved.id
    assert reports[0].title == "Top orders"
    assert reports[0].content == "Report body"


def test_find_reports_by_mention(store):
    store.save_report(
        owner="alice",
        title="Client X summary",
        content="Client X revenue grew",
    )
    store.save_report(
        owner="alice",
        title="Weekly totals",
        content="All channels combined",
    )

    matches = store.find_reports(
        "alice",
        ReportSelector(kind="mention", mention="Client X"),
    )

    assert len(matches) == 1
    assert matches[0].title == "Client X summary"


def test_find_reports_from_today(store):
    store.save_report(owner="alice", title="Today report", content="Fresh")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    with store._connect() as conn:  # noqa: SLF001 — test fixture seed
        conn.execute(
            """
            INSERT INTO reports (id, owner, title, content, question, sql, created_at, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("old-id", "alice", "Old report", "Stale", None, None, yesterday, None),
        )
        conn.commit()

    matches = store.find_reports("alice", ReportSelector(kind="today"))
    assert len(matches) == 1
    assert matches[0].title == "Today report"


def test_owner_isolation_for_list_and_delete(store):
    first = store.save_report(owner="alice", title="Alice only", content="secret")
    store.save_report(owner="bob", title="Bob only", content="private")

    assert len(store.list_reports("bob")) == 1
    assert store.list_reports("bob")[0].title == "Bob only"

    deleted = store.delete_reports("bob", [first.id])
    assert deleted == 0
    assert len(store.list_reports("alice")) == 1


def test_delete_reports_only_deletes_owner_scoped_ids(store):
    alice_report = store.save_report(owner="alice", title="Alice", content="a")
    bob_report = store.save_report(owner="bob", title="Bob", content="b")

    deleted = store.delete_reports("alice", [alice_report.id, bob_report.id])
    assert deleted == 1
    assert store.list_reports("alice") == []
    assert len(store.list_reports("bob")) == 1


@pytest.mark.parametrize(
    ("reply", "expected"),
    [
        ("yes", True),
        ("Y", True),
        ("confirm", True),
        ("delete", True),
        ("no", False),
        ("maybe", False),
        ("", False),
    ],
)
def test_is_delete_confirmed(reply, expected):
    assert is_delete_confirmed(reply) is expected
