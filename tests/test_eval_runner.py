"""Tests for dry-run eval runner."""

from __future__ import annotations

from retail_agent.evals.runner import run_suite


def test_dry_run_eval_suite_passes_with_baseline_compare():
    summary = run_suite(live=False, layer="safety", compare_baseline=False, with_judge=False)
    assert summary.failed == 0
    assert summary.passed == summary.total


def test_dry_run_eval_suite_detects_no_regressions_against_baseline():
    summary = run_suite(live=False, layer="all", compare_baseline=True, with_judge=True)
    assert summary.failed == 0
    assert summary.regressions == []
