"""Unit tests for BigQueryRunner typed results."""

from unittest.mock import MagicMock, patch

import pandas as pd

from retail_agent.bq import BigQueryRunner, QueryResult
from tests.helpers import make_settings


def test_runner_returns_guard_error_without_calling_bigquery():
    settings = make_settings()
    runner = BigQueryRunner(settings=settings)
    runner.client = MagicMock()

    result = runner.execute("DROP TABLE orders")

    assert result.ok is False
    assert "SELECT" in (result.error or "")
    runner.client.query.assert_not_called()


@patch("retail_agent.bq.bigquery.Client")
def test_runner_returns_dataframe_on_success(mock_client_cls):
    settings = make_settings()
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    mock_job = MagicMock()
    mock_job.to_dataframe.return_value = pd.DataFrame({"id": [1, 2]})
    mock_client.query.return_value = mock_job

    runner = BigQueryRunner(settings=settings)
    result = runner.execute(
        "SELECT id FROM `bigquery-public-data.thelook_ecommerce.orders` LIMIT 2"
    )

    assert result.ok is True
    assert result.empty is False
    assert list(result.dataframe.columns) == ["id"]
    mock_client.query.assert_called_once()
    _, kwargs = mock_client.query.call_args
    assert kwargs["job_config"].maximum_bytes_billed == settings.max_bytes_billed


@patch("retail_agent.bq.bigquery.Client")
def test_runner_surfaces_bigquery_errors(mock_client_cls):
    settings = make_settings()
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.query.side_effect = RuntimeError("Syntax error")

    runner = BigQueryRunner(settings=settings)
    result = runner.execute(
        "SELECT id FROM `bigquery-public-data.thelook_ecommerce.orders`"
    )

    assert result.ok is False
    assert result.error == "Syntax error"
    assert result.sql is not None


@patch("retail_agent.bq.bigquery.Client")
def test_runner_marks_empty_results(mock_client_cls):
    settings = make_settings()
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    mock_job = MagicMock()
    mock_job.to_dataframe.return_value = pd.DataFrame()
    mock_client.query.return_value = mock_job

    runner = BigQueryRunner(settings=settings)
    result = runner.execute(
        "SELECT id FROM `bigquery-public-data.thelook_ecommerce.orders` WHERE 1=0"
    )

    assert result.ok is True
    assert result.empty is True
