# MCP Server

Optional MCP (Model Context Protocol) server exposing the retail agent's **guarded** BigQuery query and Golden Bucket retrieval capabilities. Any MCP client (Cursor, Claude Desktop, other agents) can call these tools with the same safety boundaries as the CLI agent.

The core CLI prototype does **not** depend on this server — it is strictly additive.

See also: [Usage Guide](./USAGE.md), [Architecture — Extensibility](./ARCHITECTURE.md#extensibility).

## Install

From the repository root:

```bash
pip install -e ".[mcp]"
# or with dev tools:
pip install -e ".[dev,mcp]"
```

Requires the same environment as the CLI for live BigQuery:

- `GCP_PROJECT_ID` in `.env`
- `gcloud auth application-default login`

Optional: `GOOGLE_API_KEY` for embedding-based trio retrieval (otherwise keyword fallback).

## Run

Stdio transport (default for MCP clients):

```bash
retail-agent-mcp
# equivalent:
python -m retail_agent.mcp_server
```

The server reads configuration from `.env` in the repository root (same as the CLI).

## Register in Cursor

Add to your MCP config (example):

```json
{
  "mcpServers": {
    "retail-agent": {
      "command": "/absolute/path/to/opsfleet-retail-company-ai/.venv/bin/python",
      "args": ["-m", "retail_agent.mcp_server"],
      "cwd": "/absolute/path/to/opsfleet-retail-company-ai"
    }
  }
}
```

Replace paths with your clone location. Restart Cursor after saving.

## Tools

### `query_retail_data`

Execute a read-only BigQuery `SELECT` against allowed tables (`orders`, `order_items`, `products`, `users`).

| Parameter | Type | Description |
|-----------|------|-------------|
| `sql` | string | BigQuery SQL (SELECT only) |

**Safety (server-side, cannot be bypassed by clients):**

- `sql_guard` — single statement, SELECT-only, table whitelist, LIMIT injection, bytes billed cap
- `pii_mask` — email/phone columns masked before rows are returned

**Response fields:** `ok`, `sql`, `rows`, `row_count`, `masked_columns`, `pii_mask_hits`, `error`

**Example — allowed query:**

```sql
SELECT status, COUNT(*) AS n
FROM `bigquery-public-data.thelook_ecommerce.orders`
GROUP BY status
LIMIT 10
```

**Example — rejected (DML):**

```sql
DELETE FROM `bigquery-public-data.thelook_ecommerce.orders`
```

Returns `ok: false` with error `Only SELECT queries are allowed.` — no BigQuery job is submitted.

### `retrieve_trios`

Read-only Golden Bucket retrieval for few-shot grounding.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `question` | string | — | Natural-language question to match |
| `k` | integer | 3 | Number of trios (clamped 1–10) |

**Response fields:** `method` (`embedding` or `keyword`), `count`, `trios` (id, question, sql, report, tags, source_path)

Does **not** write candidate trios — curation remains in the agent graph.

## Out of scope (production only)

- Saved reports library over MCP (stateful, owner-scoped, delete confirmation)
- HTTP/SSE transports
- Authentication / authorization

These are documented in [Architecture](./ARCHITECTURE.md) as production MCP extensions.

## Verify locally

Handler unit tests:

```bash
pytest tests/test_mcp_server.py -q
```

Stdio client smoke (requires `.env` + BigQuery ADC for live PII query):

```bash
python -m retail_agent.mcp_server   # starts stdio server (Ctrl+C to exit)
```

Or run the verification script recorded in the repository's development workflow: list tools, reject DML, mask PII emails, retrieve revenue trios.

## Architecture note

This server is a **thin wrapper** over existing modules:

| Tool | Modules |
|------|---------|
| `query_retail_data` | `bq.BigQueryRunner`, `safety.mask_dataframe` |
| `retrieve_trios` | `golden.TrioStore` |

No duplicated guard or masking logic — safety lives at the MCP server boundary.
