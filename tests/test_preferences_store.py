"""Unit tests for user preference persistence."""

from __future__ import annotations

import pytest

from retail_agent.stores import ReportStore


@pytest.fixture
def store(tmp_path):
    return ReportStore(db_path=tmp_path / "agent.sqlite3")


def test_set_and_get_preferences(store):
    saved = store.set_output_format("alice", "table", notes="Prefers tabular summaries")

    prefs = store.get_preferences("alice")
    assert prefs is not None
    assert prefs.output_format == "table"
    assert prefs.notes == "Prefers tabular summaries"
    assert saved.user_id == "alice"


def test_update_preferences_overwrites_format(store):
    store.set_output_format("alice", "table")
    store.set_output_format("alice", "bullets")

    prefs = store.get_preferences("alice")
    assert prefs is not None
    assert prefs.output_format == "bullets"


def test_preferences_are_isolated_by_user(store):
    store.set_output_format("alice", "table")
    store.set_output_format("bob", "prose")

    alice = store.get_preferences("alice")
    bob = store.get_preferences("bob")

    assert alice is not None and alice.output_format == "table"
    assert bob is not None and bob.output_format == "prose"
