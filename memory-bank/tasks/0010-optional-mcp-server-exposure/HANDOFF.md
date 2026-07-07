# Handoff — Task 0010

## Summary

Delivered an optional stdio MCP server (`retail-agent-mcp`) that exposes guarded BigQuery querying and Golden Bucket trio retrieval as thin wrappers over existing modules. CLI agent behavior is unchanged; MCP is an additive install extra.

## Changed files

- `src/retail_agent/mcp_server.py` — new FastMCP server + testable handlers
- `tests/test_mcp_server.py` — handler unit tests
- `pyproject.toml` — `mcp` optional extra, `retail-agent-mcp` entry point, version **0.9.0**
- `src/retail_agent/__init__.py` — version **0.9.0**
- `docs/MCP.md` — human-facing MCP guide
- `README.md`, `docs/USAGE.md`, `docs/ARCHITECTURE.md`, `docs/TECHNICAL_EXPLANATION.md` — links and extensibility text
- `memory-bank/tasks/0010-*/` — task workflow docs

## Impact

- **Version**: 0.8.0 → **0.9.0** (minor bump per task delivery).
- **Install**: base install unchanged; MCP users run `pip install -e ".[mcp]"` or `pip install -e ".[dev,mcp]"`.
- **Runtime**: `retail-agent-mcp` starts stdio MCP server; requires same GCP/ADC env as CLI for live BigQuery.
- **Safety**: `sql_guard` and `pii_mask` enforced server-side; clients cannot bypass.
- **Out of scope**: reports library, HTTP/SSE transport, auth.

## How to verify

1. `pip install -e ".[dev,mcp]"`
2. `pytest -q` — expect **131 passed**
3. `python -m retail_agent.evals` — expect **16/16 passed** (dry-run)
4. `retail-agent-mcp` — starts stdio server (blocks; register in MCP client)
5. From MCP client:
   - `query_retail_data` with `DELETE FROM ...` → `ok=false`, guard error
   - `query_retail_data` with `SELECT email ...` → masked emails in rows
   - `retrieve_trios` with revenue question → at least one trio with `method` embedding/keyword

## Risks / rollback

- **Risk**: MCP SDK version drift — pinned `mcp>=1.28.0`; upgrade with care.
- **Risk**: Large query results over stdio — handlers return full row sets; clients should use LIMIT (guard enforces).
- **Rollback**: uninstall MCP extra; CLI and evals unaffected. Revert commit to restore 0.8.0.

## Acceptance criteria check

- [x] MCP server starts; both tools callable from real MCP client; PII masked, DML rejected — verified via SDK stdio client.
- [x] Core prototype unchanged with server absent — 131 pytest + 16/16 eval dry-run.
- [x] Human docs cover setup/usage; HLD extensibility updated to "demonstrated".
- [x] pytest green for tool handlers — `tests/test_mcp_server.py`.
