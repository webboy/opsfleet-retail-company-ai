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
retail-agent-mcp --help    # usage; exits immediately
retail-agent-mcp --version # package version
retail-agent-mcp           # blocks on stdin — normal when started by an MCP client
# equivalent:
python -m retail_agent.mcp_server
```

**Note:** Running `retail-agent-mcp` without flags produces no visible output in the terminal. The process waits on stdin for JSON-RPC messages from an MCP client. Use `--help` to confirm the install, then register the command in your MCP client config (see below).

## Register in an MCP client

Add a server entry to your MCP client's project-local configuration. The exact file location depends on the client; keep the entry scoped to this project when possible so it does not affect other workspaces.

```json
{
  "mcpServers": {
    "retail-agent": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "retail_agent.mcp_server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

`${workspaceFolder}` resolves to the project root. The app loads `.env` from the repo root automatically.

**Steps:**

1. `pip install -e ".[mcp]"` in the project venv
2. Add the JSON server entry to your MCP client's project configuration
3. Reload the MCP client
4. Confirm that `retail-agent` shows as connected and enable the tools if your client has per-tool toggles

### Absolute paths (WSL example)

```json
{
  "mcpServers": {
    "retail-agent": {
      "command": "/home/nemanja/opsfleet-retail-company-ai/.venv/bin/python",
      "args": ["-m", "retail_agent.mcp_server"],
      "cwd": "/home/nemanja/opsfleet-retail-company-ai"
    }
  }
}
```

Replace paths with your clone location. Reload your MCP client after saving.

## Tools

### `query_retail_data`

Execute a read-only BigQuery `SELECT` against allowed tables (`orders`, `order_items`, `products`, `users`).

| Parameter | Type | Description |
|-----------|------|-------------|
| `sql` | string | BigQuery SQL (SELECT only) |

**Safety (server-side, cannot be bypassed by clients):**

- `sql_guard` — single statement, SELECT-only, table whitelist, LIMIT injection/clamping, bytes billed cap
- `pii_mask` — email/phone columns masked before rows are returned
- **Response row cap** — MCP returns at most `MCP_MAX_RESPONSE_ROWS` rows (default **100**), even when BigQuery returns more after SQL guard clamping (`BQ_DEFAULT_LIMIT`, default **1000**)

**Response fields:** `ok`, `sql`, `rows`, `row_count` (full masked result size), `returned_row_count`, `response_row_limit`, `truncated`, `masked_columns`, `pii_mask_hits`, `error`

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

Or run the same checks as CI:

```bash
pytest tests/test_mcp_server.py -q
retail-agent-mcp --help
```

## Architecture note

This server is a **thin wrapper** over existing modules:

| Tool | Modules |
|------|---------|
| `query_retail_data` | `bq.BigQueryRunner`, `safety.mask_dataframe` |
| `retrieve_trios` | `golden.TrioStore` |

No duplicated guard or masking logic — safety lives at the MCP server boundary.
