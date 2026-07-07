"""Tests for eval judge parsing."""

from __future__ import annotations

from retail_agent.evals.judge import parse_judge_response, score_intent


def test_parse_judge_response_accepts_json():
    score, rationale = parse_judge_response('{"score": 4, "rationale": "Clear answer"}')
    assert score == 4
    assert rationale == "Clear answer"


def test_parse_judge_response_falls_back_to_regex():
    score, rationale = parse_judge_response("Score: {\"score\": 5, \"rationale\": \"Great\"}")
    assert score == 5


def test_score_intent_uses_dry_run_stub():
    score, rationale = score_intent(
        {"report": "Monthly revenue rose in Q4."},
        question="What was monthly revenue?",
        dry_run={"judge_score": 4, "judge_rationale": "stub"},
    )
    assert score == 4
    assert rationale == "stub"
