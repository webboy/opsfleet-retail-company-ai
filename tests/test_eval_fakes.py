"""Tests for deterministic eval fakes."""

from __future__ import annotations

from retail_agent.evals.fakes import query_result_from_spec
from retail_agent.evals.runner import _failure_diagnostics


def test_query_result_from_spec_supports_explicit_empty_rows():
    result = query_result_from_spec({"columns": ["value"], "rows": []})

    assert result.ok is True
    assert result.empty is True
    assert result.dataframe is not None
    assert result.dataframe.empty


def test_query_result_from_spec_defaults_to_single_row_when_rows_omitted():
    result = query_result_from_spec({"columns": ["value"]})

    assert result.ok is True
    assert result.empty is False
    assert result.dataframe is not None
    assert len(result.dataframe) == 1


def test_failure_diagnostics_includes_safe_query_fields():
    diagnostics = _failure_diagnostics(
        {
            "status": "fallback",
            "sql": "SELECT 1",
            "sql_attempts": 3,
            "last_error": "Unrecognized name: bad",
            "query_ok": False,
            "query_empty": False,
            "retrieved_trio_ids": ["cancelled-order-rate"],
        }
    )

    assert diagnostics == {
        "status": "fallback",
        "sql": "SELECT 1",
        "sql_attempts": 3,
        "last_error": "Unrecognized name: bad",
        "query_ok": False,
        "query_empty": False,
        "retrieved_trio_ids": ["cancelled-order-rate"],
    }
