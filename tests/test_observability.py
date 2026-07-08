"""Tests for structured observability events."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from langchain_core.messages import HumanMessage

from retail_agent.deps import AgentDeps
from retail_agent.graph import compile_graph
from retail_agent.observability import (
    TurnTracer,
    classify_error,
    events_for_turn,
    format_trace,
    snapshot_state,
    traced_node,
)
from retail_agent.bq import QueryResult
from retail_agent.stores import ReportStore
from tests.helpers import make_settings
from tests.test_graph import FakeBQRunner, ScriptLLM, _run_turn

GOOD_SQL = (
    "SELECT order_id FROM `bigquery-public-data.thelook_ecommerce.orders` LIMIT 5"
)


def test_snapshot_state_excludes_large_fields():
    state = {
        "user_id": "alice",
        "question": "Show orders",
        "result_rows": [{"order_id": 1}],
        "messages": [HumanMessage(content="Show orders")],
        "report": "Revenue grew 12% in Q1 with strong denim sales.",
    }
    snapshot = snapshot_state(state)
    assert snapshot["user_id"] == "alice"
    assert "result_rows" not in snapshot
    assert "messages" not in snapshot
    assert snapshot["report_excerpt"].startswith("Revenue grew")


def test_snapshot_state_excludes_analysis_fields_for_non_analysis_routes():
    state = {
        "user_id": "alice",
        "guard_route": "reports",
        "sql": "SELECT 1",
        "sql_attempts": 2,
        "retrieved_trio_ids": ["monthly-revenue"],
        "retrieval_method": "embedding",
    }
    snapshot = snapshot_state(state)
    assert snapshot["guard_route"] == "reports"
    assert "sql" not in snapshot
    assert "sql_attempts" not in snapshot
    assert "retrieved_trio_ids" not in snapshot
    assert "retrieval_method" not in snapshot


def test_reports_turn_trace_excludes_stale_analysis_fields(tmp_path):
    settings = make_settings(google_api_key="test-key")
    llm = ScriptLLM([f"```sql\n{GOOD_SQL}\n```", "Top orders report"])
    bq = FakeBQRunner(
        [QueryResult(ok=True, dataframe=pd.DataFrame({"order_id": [1]}), sql=GOOD_SQL)]
    )
    report_store = ReportStore(db_path=str(tmp_path / "reports.sqlite3"))
    deps = AgentDeps(
        settings=settings,
        llm=llm,
        bq_runner=bq,
        report_store=report_store,
    )
    graph = compile_graph(deps)
    config = {"configurable": {"thread_id": "thread-trace"}}

    graph.invoke(
        {
            "messages": [HumanMessage(content="Show me recent orders")],
            "user_id": "alice",
            "question": "Show me recent orders",
        },
        config,
    )

    tracer = TurnTracer(
        turn_id="reports-turn",
        user_id="alice",
        thread_id="thread-trace",
        log_path=tmp_path / "events.jsonl",
    )
    deps.tracer = tracer
    tracer.emit_turn_start("show my reports")
    graph.invoke(
        {
            "messages": [HumanMessage(content="show my reports")],
            "user_id": "alice",
            "question": "show my reports",
        },
        config,
    )
    tracer.emit_turn_end(status="done", report="Your saved reports")

    events = events_for_turn("reports-turn", log_path=tmp_path / "events.jsonl")
    node_events = [event for event in events if event.get("event_type") == "node"]
    assert node_events
    for event in node_events:
        assert "sql" not in event
        assert "retrieved_trio_ids" not in event
        assert event.get("state_after", {}).get("sql") is None
        assert event.get("state_after", {}).get("retrieved_trio_ids") is None


def test_turn_tracer_writes_node_and_turn_events(tmp_path):
    tracer = TurnTracer(
        turn_id="abc123",
        user_id="alice",
        thread_id="thread-1",
        log_path=tmp_path / "events.jsonl",
    )
    tracer.emit_turn_start("Show orders")
    tracer.emit_node_event(
        "input_guard",
        latency_ms=10.0,
        state_before={},
        state_after={"guard_decision": "allowed", "status": "running"},
    )
    tracer.emit_turn_end(status="done", report="Done")

    lines = (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    payload = [json.loads(line) for line in lines]
    assert payload[0]["event_type"] == "turn_start"
    assert payload[1]["event_type"] == "node"
    assert payload[1]["node"] == "input_guard"
    assert payload[2]["event_type"] == "turn_end"


def test_graph_wrapper_emits_events_for_happy_path(tmp_path):
    settings = make_settings(google_api_key="test-key")
    llm = ScriptLLM([f"```sql\n{GOOD_SQL}\n```", "Top orders report"])
    bq = FakeBQRunner(
        [QueryResult(ok=True, dataframe=pd.DataFrame({"order_id": [1]}), sql=GOOD_SQL)]
    )
    tracer = TurnTracer(
        turn_id="graph-turn",
        user_id="alice",
        thread_id="thread-1",
        log_path=tmp_path / "events.jsonl",
    )
    deps = AgentDeps(settings=settings, llm=llm, bq_runner=bq, tracer=tracer)

    _run_turn(deps, "Show me recent orders")

    events = events_for_turn("graph-turn", log_path=tmp_path / "events.jsonl")
    node_names = [event["node"] for event in events if event.get("event_type") == "node"]
    assert "input_guard" in node_names
    assert "compose_report" in node_names


def test_classify_error_for_guard_and_fallback():
    assert classify_error({"guard_decision": "refused"}) == "guard_refused"
    assert classify_error({"status": "fallback", "last_error": "budget exhausted"}) == "budget_exhausted"


def test_traced_node_records_exception(tmp_path):
    settings = make_settings(google_api_key="test-key")
    tracer = TurnTracer(
        turn_id="err-turn",
        user_id="alice",
        log_path=tmp_path / "events.jsonl",
    )
    deps = AgentDeps(settings=settings, llm=ScriptLLM(["x"]), bq_runner=FakeBQRunner([]), tracer=tracer)

    def boom(_state, _deps):
        raise RuntimeError("boom")

    wrapped = traced_node("boom_node", boom, deps)

    with pytest.raises(RuntimeError, match="boom"):
        wrapped({})

    events = events_for_turn("err-turn", log_path=tmp_path / "events.jsonl")
    assert events[0]["error_class"] == "RuntimeError"


def test_format_trace_renders_turn_sequence(tmp_path):
    fixture = tmp_path / "sample.jsonl"
    fixture.write_text(
        Path(__file__).parent.joinpath("fixtures", "sample_events.jsonl").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    rendered = format_trace(events_for_turn("turn-1", log_path=fixture))
    assert "START question='Show orders'" in rendered
    assert "input_guard" in rendered
    assert "END status=done" in rendered
