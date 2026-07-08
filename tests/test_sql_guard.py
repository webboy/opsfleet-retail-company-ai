"""Unit tests for sql_guard."""

import pytest

from retail_agent.bq import sql_guard
from tests.helpers import make_settings


@pytest.fixture
def settings():
    return make_settings(default_limit=500)


def test_select_on_allowed_table_passes(settings):
    sql = (
        "SELECT id, status FROM "
        "`bigquery-public-data.thelook_ecommerce.orders`"
    )
    result = sql_guard(sql, settings)
    assert result.ok is True
    assert "LIMIT 500" in result.sql


def test_existing_limit_is_preserved(settings):
    sql = (
        "SELECT id FROM `bigquery-public-data.thelook_ecommerce.orders` "
        "LIMIT 10"
    )
    result = sql_guard(sql, settings)
    assert result.ok is True
    assert "LIMIT 10" in result.sql
    assert "LIMIT 500" not in result.sql


def test_bare_allowed_table_name_passes(settings):
    sql = "SELECT id FROM orders"
    result = sql_guard(sql, settings)
    assert result.ok is True


def test_dataset_qualified_table_passes(settings):
    sql = "SELECT id FROM thelook_ecommerce.products"
    result = sql_guard(sql, settings)
    assert result.ok is True


def test_join_across_allowed_tables_passes(settings):
    sql = """
        SELECT o.id, u.id
        FROM `bigquery-public-data.thelook_ecommerce.orders` o
        JOIN `bigquery-public-data.thelook_ecommerce.users` u
          ON o.user_id = u.id
    """
    result = sql_guard(sql, settings)
    assert result.ok is True


def test_dml_is_blocked(settings):
    result = sql_guard(
        "INSERT INTO `bigquery-public-data.thelook_ecommerce.orders` VALUES (1)",
        settings,
    )
    assert result.ok is False
    assert "SELECT" in result.error


def test_ddl_is_blocked(settings):
    result = sql_guard(
        "CREATE TABLE `bigquery-public-data.thelook_ecommerce.orders` (id INT64)",
        settings,
    )
    assert result.ok is False


def test_multi_statement_is_blocked(settings):
    result = sql_guard(
        "SELECT 1; SELECT 2 FROM `bigquery-public-data.thelook_ecommerce.orders`",
        settings,
    )
    assert result.ok is False
    assert "Multiple" in result.error


def test_non_allowed_table_is_blocked(settings):
    result = sql_guard(
        "SELECT * FROM `bigquery-public-data.thelook_ecommerce.secret_table`",
        settings,
    )
    assert result.ok is False
    assert "not allowed" in result.error.lower()


def test_non_allowed_dataset_is_blocked(settings):
    result = sql_guard(
        "SELECT * FROM `bigquery-public-data.other_dataset.orders`",
        settings,
    )
    assert result.ok is False


def test_empty_sql_is_blocked(settings):
    result = sql_guard("   ", settings)
    assert result.ok is False
    assert result.error == "Empty SQL."


def test_non_sql_prose_is_blocked(settings):
    result = sql_guard(
        "a you'd like to retrieve from the BigQuery tables",
        settings,
    )
    assert result.ok is False
    assert "parse error" in (result.error or "").lower()


def test_cte_over_allowed_table_passes(settings):
    sql = """
        WITH monthly AS (
          SELECT DATE_TRUNC(DATE(created_at), MONTH) AS m, SUM(sale_price) AS rev
          FROM `bigquery-public-data.thelook_ecommerce.order_items`
          GROUP BY m
        )
        SELECT * FROM monthly ORDER BY m
    """
    result = sql_guard(sql, settings)
    assert result.ok is True
    assert "LIMIT 500" in result.sql


def test_cte_body_with_disallowed_table_is_blocked(settings):
    sql = """
        WITH leaked AS (
          SELECT * FROM `bigquery-public-data.thelook_ecommerce.secret_table`
        )
        SELECT * FROM leaked
    """
    result = sql_guard(sql, settings)
    assert result.ok is False
    assert "not allowed" in (result.error or "").lower()


def test_bare_disallowed_non_cte_table_still_blocked(settings):
    sql = """
        WITH monthly AS (
          SELECT id FROM `bigquery-public-data.thelook_ecommerce.orders`
        )
        SELECT * FROM secret_table
    """
    result = sql_guard(sql, settings)
    assert result.ok is False
    assert "not allowed" in (result.error or "").lower()


def test_multiple_nested_ctes_pass(settings):
    sql = """
        WITH base AS (
          SELECT order_id, sale_price
          FROM `bigquery-public-data.thelook_ecommerce.order_items`
        ),
        agg AS (
          SELECT order_id, SUM(sale_price) AS total
          FROM base
          GROUP BY order_id
        )
        SELECT * FROM agg
    """
    result = sql_guard(sql, settings)
    assert result.ok is True
