"""Tests for deterministic eval fakes."""

from __future__ import annotations

from retail_agent.config import Settings
from retail_agent.evals.fakes import query_result_from_spec
from retail_agent.evals.runner import _failure_diagnostics, _validate_live_llm_settings


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


def test_validate_live_llm_settings_rejects_missing_openrouter_key():
    settings = Settings(
        gcp_project_id="proj",
        google_api_key="key",
        model="gemini-2.5-flash",
        embedding_model="gemini-embedding-001",
        persona="default",
        provider="gemini",
        fallback_provider="openrouter",
        openrouter_api_key=None,
        openrouter_model="openrouter/auto",
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

    try:
        _validate_live_llm_settings(settings)
    except ValueError as exc:
        assert "OPENROUTER_API_KEY is missing" in str(exc)
    else:
        raise AssertionError("expected ValueError for missing OpenRouter key")
