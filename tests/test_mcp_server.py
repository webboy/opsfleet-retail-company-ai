"""Unit tests for MCP server tool handlers."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from retail_agent.bq import BigQueryRunner, QueryResult
from retail_agent.golden import FakeEmbedder, TrioStore
from retail_agent.mcp_server import (
    build_arg_parser,
    query_retail_data_handler,
    retrieve_trios_handler,
)
from tests.helpers import make_settings
from tests.test_golden import OTHER_TRIO, SAMPLE_TRIO


def _bucket_dir(tmp_path: Path) -> Path:
    (tmp_path / "sample.md").write_text(SAMPLE_TRIO, encoding="utf-8")
    (tmp_path / "monthly.md").write_text(OTHER_TRIO, encoding="utf-8")
    return tmp_path


def test_query_retail_data_rejects_dml_without_bigquery_call():
    settings = make_settings()
    runner = BigQueryRunner(settings=settings)
    runner.client = MagicMock()

    payload = query_retail_data_handler("DROP TABLE orders", runner=runner)

    assert payload["ok"] is False
    assert "SELECT" in (payload["error"] or "")
    assert payload["rows"] == []
    runner.client.query.assert_not_called()


def test_query_retail_data_masks_pii_columns():
    settings = make_settings()
    runner = BigQueryRunner(settings=settings)
    runner.execute = MagicMock(
        return_value=QueryResult(
            ok=True,
            dataframe=pd.DataFrame(
                {
                    "email": ["alice@example.com"],
                    "total_spend": [100.0],
                }
            ),
            sql="SELECT email, total_spend FROM users LIMIT 1",
            empty=False,
        )
    )

    payload = query_retail_data_handler(
        "SELECT email, total_spend FROM users LIMIT 1",
        runner=runner,
    )

    assert payload["ok"] is True
    assert payload["masked_columns"] == ["email"]
    assert payload["pii_mask_hits"] == 1
    assert payload["row_count"] == 1
    assert payload["returned_row_count"] == 1
    assert payload["response_row_limit"] == settings.mcp_max_response_rows
    assert payload["truncated"] is False
    assert "alice@example.com" not in json.dumps(payload["rows"])
    assert "@***.***" in payload["rows"][0]["email"]


def test_query_retail_data_truncates_large_payloads():
    settings = make_settings(mcp_max_response_rows=2)
    runner = BigQueryRunner(settings=settings)
    runner.execute = MagicMock(
        return_value=QueryResult(
            ok=True,
            dataframe=pd.DataFrame({"id": [1, 2, 3, 4, 5]}),
            sql="SELECT id FROM orders LIMIT 5",
            empty=False,
        )
    )

    payload = query_retail_data_handler(
        "SELECT id FROM orders LIMIT 5",
        runner=runner,
        max_response_rows=2,
    )

    assert payload["ok"] is True
    assert payload["row_count"] == 5
    assert payload["returned_row_count"] == 2
    assert payload["response_row_limit"] == 2
    assert payload["truncated"] is True
    assert len(payload["rows"]) == 2
    assert payload["rows"][0]["id"] == 1
    assert payload["rows"][1]["id"] == 2


def test_query_retail_data_preserves_numeric_revenue():
    settings = make_settings()
    runner = BigQueryRunner(settings=settings)
    runner.execute = MagicMock(
        return_value=QueryResult(
            ok=True,
            dataframe=pd.DataFrame(
                {
                    "month": ["2025-07"],
                    "revenue": [51664.79010748863],
                }
            ),
            sql="SELECT month, revenue FROM orders LIMIT 1",
            empty=False,
        )
    )

    payload = query_retail_data_handler("SELECT month, revenue FROM orders LIMIT 1", runner=runner)

    assert payload["ok"] is True
    assert payload["masked_columns"] == []
    assert payload["rows"][0]["revenue"] == 51664.79010748863


def test_retrieve_trios_returns_expected_shape(tmp_path: Path):
    bucket_dir = _bucket_dir(tmp_path)
    store = TrioStore(
        bucket_dir=bucket_dir,
        embedder=FakeEmbedder(),
        settings=make_settings(),
    )

    payload = retrieve_trios_handler(
        "What was monthly revenue last year?",
        k=2,
        store=store,
    )

    assert payload["error"] is None
    assert payload["method"] == "embedding"
    assert payload["count"] == 1
    assert payload["trios"][0]["id"] == "monthly-revenue"
    assert {"id", "question", "sql", "report", "tags"} <= set(payload["trios"][0])


def test_retrieve_trios_works_when_bucket_has_malformed_file(tmp_path: Path):
    bucket_dir = _bucket_dir(tmp_path)
    (bucket_dir / "zz-broken.md").write_text(
        "---\nquestion: broken\nsql: SELECT 1\n---\nbody\n",
        encoding="utf-8",
    )
    store = TrioStore(
        bucket_dir=bucket_dir,
        embedder=FakeEmbedder(),
        settings=make_settings(),
    )

    payload = retrieve_trios_handler("monthly revenue last year", k=2, store=store)

    assert payload["error"] is None
    assert payload["count"] == 1
    assert {trio["id"] for trio in payload["trios"]} == {"monthly-revenue"}


def test_retrieve_trios_clamps_k_and_rejects_empty_question(tmp_path: Path):
    bucket_dir = _bucket_dir(tmp_path)
    store = TrioStore(
        bucket_dir=bucket_dir,
        embedder=FakeEmbedder(),
        settings=make_settings(),
    )

    empty_payload = retrieve_trios_handler("  ", store=store)
    assert empty_payload["count"] == 0
    assert empty_payload["error"]

    clamped = retrieve_trios_handler("monthly revenue", k=99, store=store)
    assert clamped["count"] <= 10


def test_cli_help_and_version(capsys):
    parser = build_arg_parser()

    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--help"])
    assert exc.value.code == 0
    help_text = capsys.readouterr().out
    assert "retail-agent-mcp" in help_text
    assert "stdio" in help_text.lower()

    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--version"])
    assert exc.value.code == 0
    version_text = capsys.readouterr().out
    assert "retail-agent-mcp" in version_text
