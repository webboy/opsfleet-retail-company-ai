# Handoff — Task 0022

## Summary

Implemented SQL cost controls and MCP payload caps. `sql_guard` now clamps explicit oversized `LIMIT` values to `BQ_DEFAULT_LIMIT` (default 1000). MCP `query_retail_data` masks the full result set but returns at most `MCP_MAX_RESPONSE_ROWS` (default 100) with explicit truncation metadata.

## Changed files

- `src/retail_agent/bq.py` — LIMIT injection/clamping helpers
- `src/retail_agent/config.py` — `MCP_MAX_RESPONSE_ROWS` setting
- `src/retail_agent/mcp_server.py` — MCP response truncation + metadata
- `src/retail_agent/__init__.py`, `pyproject.toml` — version `0.20.0`
- `.env.example` — document `MCP_MAX_RESPONSE_ROWS`
- `tests/test_sql_guard.py`, `tests/test_mcp_server.py`, `tests/helpers.py`
- `docs/MCP.md`, `docs/TECHNICAL_EXPLANATION.md`, `docs/ARCHITECTURE.md`, `docs/EVALUATION.md`
- Eval/judge Settings constructors updated for new config field

## Impact

- **CLI/agent path:** BigQuery jobs can no longer execute with explicit `LIMIT 1000000`; they are rewritten to the configured cap before execution.
- **MCP path:** Tool responses stay bounded even when SQL guard allows up to 1000 rows; clients see `truncated: true` and both total/returned row counts.
- **Config:** `BQ_DEFAULT_LIMIT` = SQL hard max; `MCP_MAX_RESPONSE_ROWS` = MCP payload cap (independent).
- **Version:** `0.20.0`

## How to verify

1. `pytest tests/test_sql_guard.py tests/test_mcp_server.py -q`
2. `pytest -q`
3. `python -m retail_agent.evals`
4. Optional manual check:
   ```python
   from retail_agent.bq import sql_guard
   from tests.helpers import make_settings
   s = make_settings(default_limit=500)
   print(sql_guard("SELECT id FROM orders LIMIT 1000000", s).sql)
   # expect LIMIT 500
   ```

## Risks / rollback

- Clamping non-literal limits (e.g. subquery parameters) to the hard cap is intentional for deterministic safety; revert only if a legitimate use case needs dynamic limits.
- MCP clients that assumed `row_count == len(rows)` must use `returned_row_count` for payload size and `row_count` for full result size.

## Acceptance criteria check

- [x] All criteria verified during implementation; user approved 2026-07-08.
