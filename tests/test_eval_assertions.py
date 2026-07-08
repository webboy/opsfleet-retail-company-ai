"""Tests for eval property assertions."""

from __future__ import annotations

from retail_agent.evals.assertions import evaluate_expectations, tables_in_sql


def test_tables_in_sql_extracts_allowed_tables():
    sql = (
        "SELECT o.order_id FROM `bigquery-public-data.thelook_ecommerce.orders` o "
        "JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi ON o.order_id = oi.order_id"
    )
    assert tables_in_sql(sql) == {"orders", "order_items"}


def test_evaluate_expectations_passes_matching_state():
    result = evaluate_expectations(
        {"status": "done", "sql": "SELECT 1 FROM `bigquery-public-data.thelook_ecommerce.orders`", "report": "Revenue by month"},
        {"status": "done", "sql_tables": ["orders"], "report_must_contain": ["Revenue"]},
        bq_calls=1,
    )
    assert result.passed


def test_evaluate_expectations_detects_failures():
    result = evaluate_expectations(
        {"status": "fallback", "guard_decision": "allowed", "report": "nope"},
        {
            "status": "done",
            "guard_decision": "refused",
            "report_must_contain": ["revenue"],
            "max_bq_calls": 0,
        },
        bq_calls=2,
    )
    assert not result.passed
    assert len(result.failures) >= 3


def test_evaluate_expectations_requires_empty_result_when_expected():
    result = evaluate_expectations(
        {"status": "done", "query_ok": True, "query_empty": False, "report": "Found orders."},
        {"query_empty": True},
    )
    assert not result.passed
    assert "expected query_empty=True" in result.failures
