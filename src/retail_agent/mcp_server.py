"""MCP server exposing guarded BigQuery query and Golden Bucket retrieval."""

from __future__ import annotations

import json
import logging
from typing import Any

from retail_agent.bq import BigQueryRunner
from retail_agent.golden import TrioStore
from retail_agent.safety import mask_dataframe

logger = logging.getLogger(__name__)

MIN_TOP_K = 1
MAX_TOP_K = 10
DEFAULT_TOP_K = 3


def _json_safe(value: object) -> object:
    """Convert pandas/numpy scalars to JSON-serializable Python types."""

    if value is None:
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass
    return value


def _dataframe_to_rows(df) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in df.to_dict(orient="records"):
        records.append({key: _json_safe(val) for key, val in row.items()})
    return records


def query_retail_data_handler(
    sql: str,
    *,
    runner: BigQueryRunner | None = None,
) -> dict[str, Any]:
    """Execute guarded SQL, mask PII in results, return JSON-serializable payload."""

    runner = runner or BigQueryRunner()
    result = runner.execute(sql)

    if not result.ok:
        return {
            "ok": False,
            "sql": result.sql,
            "rows": [],
            "row_count": 0,
            "masked_columns": [],
            "pii_mask_hits": 0,
            "error": result.error,
        }

    assert result.dataframe is not None
    masked = mask_dataframe(result.dataframe)
    rows = _dataframe_to_rows(masked.dataframe)

    return {
        "ok": True,
        "sql": result.sql,
        "rows": rows,
        "row_count": len(rows),
        "empty": result.empty,
        "masked_columns": list(masked.masked_columns),
        "pii_mask_hits": masked.mask_hit_count,
        "error": None,
    }


def retrieve_trios_handler(
    question: str,
    k: int = DEFAULT_TOP_K,
    *,
    store: TrioStore | None = None,
) -> dict[str, Any]:
    """Read-only Golden Bucket retrieval for MCP clients."""

    question = (question or "").strip()
    if not question:
        return {
            "method": "keyword",
            "count": 0,
            "trios": [],
            "error": "Question must not be empty.",
        }

    clamped_k = max(MIN_TOP_K, min(int(k), MAX_TOP_K))
    store = store or TrioStore()
    retrieval = store.retrieve(question, k=clamped_k)

    return {
        "method": retrieval.method,
        "count": len(retrieval.trios),
        "trios": [trio.to_dict() for trio in retrieval.trios],
        "error": None,
    }


def create_mcp_server():
    """Build FastMCP server with retail agent tools."""

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP(
        "retail-agent",
        instructions=(
            "Guarded retail analytics tools. SQL is read-only with table whitelist "
            "and PII masking enforced server-side. Golden Bucket retrieval is read-only."
        ),
    )

    @mcp.tool(
        name="query_retail_data",
        description=(
            "Run a read-only BigQuery SELECT against thelook_ecommerce tables "
            "(orders, order_items, products, users). DML/DDL is rejected. "
            "PII columns are masked in returned rows."
        ),
    )
    def query_retail_data(sql: str) -> str:
        payload = query_retail_data_handler(sql)
        return json.dumps(payload, indent=2, default=str)

    @mcp.tool(
        name="retrieve_trios",
        description=(
            "Retrieve top-k similar Golden Bucket trios (question, SQL, report) "
            "for few-shot grounding. Read-only; does not write candidates."
        ),
    )
    def retrieve_trios(question: str, k: int = DEFAULT_TOP_K) -> str:
        payload = retrieve_trios_handler(question, k=k)
        return json.dumps(payload, indent=2, default=str)

    return mcp


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    server = create_mcp_server()
    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
