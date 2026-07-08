"""MCP server exposing guarded BigQuery query and Golden Bucket retrieval."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any

from retail_agent import __version__
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
    max_response_rows: int | None = None,
) -> dict[str, Any]:
    """Execute guarded SQL, mask PII in results, return JSON-serializable payload."""

    runner = runner or BigQueryRunner()
    response_row_limit = max_response_rows
    if response_row_limit is None:
        response_row_limit = runner.settings.mcp_max_response_rows
    result = runner.execute(sql)

    if not result.ok:
        return {
            "ok": False,
            "sql": result.sql,
            "rows": [],
            "row_count": 0,
            "returned_row_count": 0,
            "response_row_limit": response_row_limit,
            "truncated": False,
            "masked_columns": [],
            "pii_mask_hits": 0,
            "error": result.error,
        }

    assert result.dataframe is not None
    masked = mask_dataframe(result.dataframe)
    total_rows = len(masked.dataframe)
    truncated_df = masked.dataframe.head(response_row_limit)
    rows = _dataframe_to_rows(truncated_df)

    return {
        "ok": True,
        "sql": result.sql,
        "rows": rows,
        "row_count": total_rows,
        "returned_row_count": len(rows),
        "response_row_limit": response_row_limit,
        "truncated": total_rows > response_row_limit,
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
            "PII columns are masked in returned rows. Response payloads are "
            "capped by MCP_MAX_RESPONSE_ROWS with truncation metadata."
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


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="retail-agent-mcp",
        description=(
            "Stdio MCP server exposing guarded BigQuery query and Golden Bucket retrieval."
        ),
        epilog=(
            "With no arguments the process blocks on stdin waiting for an MCP client "
            "(stdio transport). That is expected — register this command in your MCP "
            "client config instead of running it interactively."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    server = create_mcp_server()
    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
