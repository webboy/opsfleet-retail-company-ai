"""Tests for trace CLI."""

from __future__ import annotations

from pathlib import Path

from retail_agent.trace import main as trace_main


def test_trace_cli_renders_known_turn(tmp_path, capsys):
    log_path = tmp_path / "events.jsonl"
    log_path.write_text(
        Path(__file__).parent.joinpath("fixtures", "sample_events.jsonl").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    exit_code = trace_main(["turn-1", "--log-path", str(log_path)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Turn turn-1" in output
    assert "input_guard" in output


def test_trace_cli_missing_turn_returns_error(tmp_path, capsys):
    log_path = tmp_path / "events.jsonl"
    log_path.write_text("", encoding="utf-8")

    exit_code = trace_main(["missing", "--log-path", str(log_path)])
    assert exit_code == 1
