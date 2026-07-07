"""Tests for eval baseline comparison."""

from __future__ import annotations

from retail_agent.evals.baseline import compare_runs


def test_compare_runs_flags_pass_regression():
    baseline = {
        "monthly-revenue": {"case_id": "monthly-revenue", "passed": True, "judge_score": 4},
    }
    current = [
        {"case_id": "monthly-revenue", "passed": False, "judge_score": 4},
    ]
    comparison = compare_runs(current, baseline)
    assert comparison.has_regressions
    assert comparison.regressions[0].case_id == "monthly-revenue"


def test_compare_runs_flags_score_drop():
    baseline = {
        "monthly-revenue": {"case_id": "monthly-revenue", "passed": True, "judge_score": 5},
    }
    current = [
        {"case_id": "monthly-revenue", "passed": True, "judge_score": 2},
    ]
    comparison = compare_runs(current, baseline, score_tolerance=1)
    assert comparison.has_regressions
