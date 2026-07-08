"""Tests for dry-run eval runner."""

from __future__ import annotations

from unittest.mock import patch

from retail_agent.evals.runner import run_suite


def test_dry_run_eval_suite_passes_with_baseline_compare():
    summary = run_suite(live=False, layer="safety", compare_baseline=False, with_judge=False)
    assert summary.failed == 0
    assert summary.passed == summary.total


def test_dry_run_eval_suite_detects_no_regressions_against_baseline():
    summary = run_suite(live=False, layer="all", compare_baseline=True, with_judge=True)
    assert summary.failed == 0
    assert summary.regressions == []


def test_dry_run_safety_layer_has_no_phantom_baseline_regressions():
    summary = run_suite(live=False, layer="safety", compare_baseline=True, with_judge=False)
    assert summary.failed == 0
    assert summary.regressions == []
    assert summary.total == 5


def test_low_judge_score_fails_capability_case():
    with patch(
        "retail_agent.evals.runner.score_intent",
        return_value=(2, "Report misses the monthly trend."),
    ):
        summary = run_suite(
            live=False,
            layer="capability",
            compare_baseline=False,
            with_judge=True,
        )
    monthly = next(item for item in summary.results if item.case_id == "monthly-revenue")
    assert monthly.passed is False
    assert any("judge score too low" in failure for failure in monthly.failures)


def test_judge_unavailable_does_not_fail_by_default():
    with patch(
        "retail_agent.evals.runner.score_intent",
        return_value=(None, "judge unavailable: RuntimeError: connection refused"),
    ):
        summary = run_suite(
            live=False,
            layer="capability",
            compare_baseline=False,
            with_judge=True,
            require_judge=False,
        )

    judged = [item for item in summary.results if item.judge_score is None and item.judge_rationale]
    assert judged
    assert all(item.passed for item in judged)


def test_require_judge_fails_when_scoring_unavailable():
    with patch(
        "retail_agent.evals.runner.score_intent",
        return_value=(None, "judge unavailable: RuntimeError: connection refused"),
    ):
        summary = run_suite(
            live=False,
            layer="capability",
            compare_baseline=False,
            with_judge=True,
            require_judge=True,
        )

    failed = [item for item in summary.results if "judge unavailable (required)" in item.failures]
    assert failed
    assert summary.failed >= len(failed)


def test_valid_empty_result_case_passes_in_suite():
    summary = run_suite(live=False, layer="all", compare_baseline=False, with_judge=True)
    empty_case = next(item for item in summary.results if item.case_id == "valid-empty-result")
    assert empty_case.passed is True
    assert empty_case.judge_score == 3


def test_cancelled_order_rate_exhaustion_matches_live_failure_pattern():
    """Regression evidence for live `cancelled-order-rate` NL-to-SQL weakness (no credentials)."""
    from pathlib import Path

    from retail_agent.config import Settings
    from retail_agent.deps import AgentDeps
    from retail_agent.evals.fakes import FakeBQRunner, QueryResult, ScriptLLM
    from retail_agent.golden import FakeEmbedder, TrioStore
    from retail_agent.graph import compile_graph
    from langchain_core.messages import HumanMessage

    bad_sql = (
        "SELECT COUNTIF(status = 'Cancelled') / COUNT(*) AS cancelled_rate, total_orders "
        "FROM `bigquery-public-data.thelook_ecommerce.orders` "
        "GROUP BY total_orders"
    )
    settings = Settings(
        gcp_project_id="eval-project",
        google_api_key="eval-key",
        model="gemini-2.5-flash",
        embedding_model="gemini-embedding-001",
        persona="default",
        provider="gemini",
        fallback_provider=None,
        openrouter_api_key=None,
        openrouter_model="google/gemini-2.0-flash-exp:free",
        ollama_host="http://localhost:11434",
        ollama_model="llama3.2",
        dataset_id="bigquery-public-data.thelook_ecommerce",
        reports_db_path=None,
        personas_dir=None,
        max_bytes_billed=1_073_741_824,
        default_limit=1000,
        mcp_max_response_rows=100,
        embedding_min_similarity=0.35,
        keyword_min_overlap=2,
    )
    llm = ScriptLLM([f"```sql\n{bad_sql}\n```"] * 3)
    bq = FakeBQRunner(
        [QueryResult(ok=False, error="Unrecognized name: total_orders in GROUP BY", sql=bad_sql)] * 3
    )
    bucket_dir = Path(__file__).resolve().parents[1] / "golden_bucket"
    deps = AgentDeps(
        settings=settings,
        llm=llm,
        bq_runner=bq,
        max_sql_attempts=3,
        trio_store=TrioStore(bucket_dir, settings=settings, embedder=FakeEmbedder()),
    )
    graph = compile_graph(deps)
    state = graph.invoke(
        {
            "messages": [HumanMessage(content="What share of orders are cancelled?")],
            "user_id": "alice",
            "question": "What share of orders are cancelled?",
        },
        {"configurable": {"thread_id": "eval-cancelled-exhaustion"}},
    )

    assert state["status"] == "fallback"
    assert state.get("query_ok") is False
    assert state.get("query_empty") is False
    assert state.get("sql_attempts") == 3
    assert "cancelled-order-rate" in (state.get("retrieved_trio_ids") or [])
