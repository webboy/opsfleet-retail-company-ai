# Plan — Task 0010

Concrete implementation plan (approved 2026-07-08).

## Steps

1. Mark task `in_progress`; sync `INDEX.md`.
2. Add optional `mcp` extra in `pyproject.toml` and `retail-agent-mcp` console script.
3. Implement `src/retail_agent/mcp_server.py`:
   - `query_retail_data_handler(sql)` → `BigQueryRunner.execute()` + `mask_dataframe()`
   - `retrieve_trios_handler(question, k)` → `TrioStore.retrieve()`
   - FastMCP stdio server registering both tools.
4. Add `tests/test_mcp_server.py` for handler-level guard/mask/retrieval tests.
5. Real MCP stdio client verification; record in WORKLOG/HANDOFF.
6. Add `docs/MCP.md`; link from README/USAGE; update ARCHITECTURE extensibility.
7. Bump version `0.8.0` → `0.9.0`; pytest + evals; commit; `pending_review`.

## Out of scope

Reports library MCP, HTTP/SSE transport, auth.
