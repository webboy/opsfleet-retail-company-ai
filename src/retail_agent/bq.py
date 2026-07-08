"""BigQuery access with deterministic SQL guardrails."""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import sqlglot
from google.cloud import bigquery
from sqlglot import exp

from retail_agent.config import Settings, get_settings

logger = logging.getLogger(__name__)

ALLOWED_PROJECT = "bigquery-public-data"
ALLOWED_DATASET = "thelook_ecommerce"


@dataclass(frozen=True)
class GuardResult:
    """Outcome of static SQL validation."""

    ok: bool
    sql: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class QueryResult:
    """Outcome of a guarded BigQuery execution."""

    ok: bool
    dataframe: pd.DataFrame | None = None
    sql: str | None = None
    error: str | None = None
    empty: bool = False


def sql_guard(sql: str, settings: Settings) -> GuardResult:
    """Validate and sanitize SQL before BigQuery execution."""

    raw = sql.strip()
    if not raw:
        return GuardResult(ok=False, error="Empty SQL.")

    try:
        statements = sqlglot.parse(raw, read="bigquery")
    except sqlglot.errors.SqlglotError as exc:
        return GuardResult(ok=False, error=f"SQL parse error: {exc}")

    if len(statements) != 1:
        return GuardResult(ok=False, error="Multiple SQL statements are not allowed.")

    expression = statements[0]
    if not _is_read_query(expression):
        return GuardResult(ok=False, error="Only SELECT queries are allowed.")

    cte_names = _collect_cte_names(expression)

    for table in expression.find_all(exp.Table):
        if not _table_allowed(table, settings, cte_names):
            return GuardResult(
                ok=False,
                error=f"Table not allowed: {_table_label(table)}",
            )

    if expression.args.get("limit") is None:
        expression = expression.limit(settings.default_limit)

    sanitized = expression.sql(dialect="bigquery")
    return GuardResult(ok=True, sql=sanitized)


def _is_read_query(expression: exp.Expression) -> bool:
    if isinstance(expression, exp.Select):
        return True
    if isinstance(expression, exp.Union):
        return True
    return False


def _collect_cte_names(expression: exp.Expression) -> frozenset[str]:
    names: set[str] = set()
    for cte in expression.find_all(exp.CTE):
        alias = cte.alias_or_name
        if alias:
            names.add(_normalize(alias))
    return frozenset(names)


def _table_allowed(
    table: exp.Table,
    settings: Settings,
    cte_names: frozenset[str] = frozenset(),
) -> bool:
    catalog = _normalize(table.catalog)
    db = _normalize(table.db)
    name = _normalize(table.name)

    if not name:
        return False

    # Bare CTE alias reference — allowed when defined in WITH clause.
    if not catalog and not db and name in cte_names:
        return True

    if name not in settings.allowed_tables:
        return False

    if catalog and db:
        return catalog == ALLOWED_PROJECT and db == ALLOWED_DATASET

    if db:
        return db == ALLOWED_DATASET

    # Bare table name — allowed only when it matches the whitelist.
    return not catalog and not db


def _table_label(table: exp.Table) -> str:
    parts = [table.catalog, table.db, table.name]
    return ".".join(part for part in parts if part)


def _normalize(value: str | None) -> str:
    return value.lower() if value else ""


class BigQueryRunner:
    """Execute guarded SQL against BigQuery and return typed results."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.project_id = project_id or self.settings.gcp_project_id
        self.dataset_id = dataset_id or self.settings.dataset_id
        self.client = bigquery.Client(project=self.project_id)

    def execute(self, sql: str) -> QueryResult:
        """Run SQL through the guard, then execute on BigQuery."""

        guard = sql_guard(sql, self.settings)
        if not guard.ok:
            logger.warning("sql_guard blocked query: %s", guard.error)
            return QueryResult(ok=False, error=guard.error, sql=sql)

        assert guard.sql is not None
        job_config = bigquery.QueryJobConfig(
            maximum_bytes_billed=self.settings.max_bytes_billed,
        )

        try:
            query_job = self.client.query(guard.sql, job_config=job_config)
            dataframe = query_job.to_dataframe(create_bqstorage_client=False)
            return QueryResult(
                ok=True,
                dataframe=dataframe,
                sql=guard.sql,
                empty=dataframe.empty,
            )
        except Exception as exc:  # noqa: BLE001 — surface as typed result
            logger.exception("BigQuery query failed")
            return QueryResult(ok=False, error=str(exc), sql=guard.sql)


def _main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        sql = (
            "SELECT order_id, status FROM "
            "`bigquery-public-data.thelook_ecommerce.orders` LIMIT 5"
        )
    else:
        sql = sys.argv[1]

    runner = BigQueryRunner()
    result = runner.execute(sql)

    if not result.ok:
        print(f"ERROR: {result.error}", file=sys.stderr)
        if result.sql:
            print(f"SQL: {result.sql}", file=sys.stderr)
        return 1

    assert result.dataframe is not None
    print(result.dataframe.to_string(index=False))
    print(f"\nrows={len(result.dataframe)} empty={result.empty}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
