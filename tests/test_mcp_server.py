"""Unit tests for MCP server tool handlers."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from retail_agent.bq import BigQueryRunner, QueryResult
from retail_agent.golden import FakeEmbedder, TrioStore
from retail_agent.mcp_server import (
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
    assert "alice@example.com" not in json.dumps(payload["rows"])
    assert "@***.***" in payload["rows"][0]["email"]


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
    assert payload["count"] == 2
    assert payload["trios"][0]["id"] in {"monthly-revenue", "sample-trio"}
    assert {"id", "question", "sql", "report", "tags"} <= set(payload["trios"][0])


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
