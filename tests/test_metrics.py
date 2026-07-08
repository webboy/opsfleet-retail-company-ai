"""Tests for metrics aggregation."""

from __future__ import annotations

from pathlib import Path

from retail_agent.metrics import main as metrics_main
from retail_agent.observability import aggregate_metrics, load_events


def test_aggregate_metrics_from_sample_events():
    events = load_events(Path(__file__).parent / "fixtures" / "sample_events.jsonl")
    metrics = aggregate_metrics(events)

    assert metrics["total_turns"] == 2
    assert metrics["turn_success_rate"] == 0.5
    assert metrics["guard_block_rate"] == 0.5
    assert metrics["self_heal_events"] == 1
    assert metrics["pii_mask_hits"] == 2
    assert metrics["latency_ms"]["count"] == 4


def test_aggregate_metrics_counts_self_heal_per_turn_not_per_node():
    events = [
        {
            "event_type": "node",
            "turn_id": "turn-heal",
            "node": "generate_sql",
            "latency_ms": 10.0,
            "sql_attempts": 2,
        },
        {
            "event_type": "node",
            "turn_id": "turn-heal",
            "node": "execute_bq",
            "latency_ms": 12.0,
            "sql_attempts": 2,
        },
        {
            "event_type": "node",
            "turn_id": "turn-heal",
            "node": "compose_report",
            "latency_ms": 8.0,
            "sql_attempts": 2,
        },
        {
            "event_type": "turn_end",
            "turn_id": "turn-heal",
            "status": "done",
        },
    ]
    metrics = aggregate_metrics(events)
    assert metrics["self_heal_events"] == 1


def test_metrics_cli_prints_summary(tmp_path, capsys):
    log_path = tmp_path / "events.jsonl"
    log_path.write_text(
        Path(__file__).parent.joinpath("fixtures", "sample_events.jsonl").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    exit_code = metrics_main(["--log-path", str(log_path)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "success_rate" in output
    assert "self_heal_events: 1" in output
