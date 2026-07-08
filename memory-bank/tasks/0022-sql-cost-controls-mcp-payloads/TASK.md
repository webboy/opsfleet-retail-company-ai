# Task 0022 — SQL cost controls and MCP payload caps

## Metadata

- **Task ID**: 0022
- **Title**: SQL cost controls and MCP payload caps
- **Status**: pending_review
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Close the reviewer-identified cost and payload risks in guarded BigQuery execution and the optional MCP server. The agent must not allow explicit large `LIMIT` values or unbounded MCP row payloads to inflate memory, stdout, or downstream tool usage.

## Scope

- Clamp existing SQL `LIMIT` values to the configured/default maximum instead of only injecting a missing limit.
- Add tests proving missing, small, and oversized limits are handled correctly.
- Cap MCP `query_retail_data` returned rows independently of BigQuery execution result size.
- Document the row/limit behavior in human-facing docs where MCP or SQL guardrails are described.
- Consider adding BigQuery job timeout configuration if it can be done cleanly without expanding the task too much.

### Out of scope

- Reworking the whole SQL generation prompt.
- Adding authentication to the MCP server.
- Changing allowed table policy.

## Acceptance criteria

- [x] `sql_guard` preserves small explicit limits but clamps oversized explicit limits.
- [x] Queries without a limit still receive the default limit.
- [x] MCP `query_retail_data` returns at most the configured/documented response row cap and reports the original result count or truncation state clearly.
- [x] Unit tests cover SQL limit injection/clamping and MCP payload truncation.
- [x] Relevant docs mention the practical result-row and cost controls.
- [x] `pytest -q` and `python -m retail_agent.evals` pass.

## References

- Review finding: SQL guard does not cap explicit large `LIMIT`.
- Review finding: MCP `query_retail_data` returns unbounded row payloads.
- Code: `src/retail_agent/bq.py`, `src/retail_agent/mcp_server.py`, `tests/test_sql_guard.py`, `tests/test_mcp_server.py`.
- Assignment requirement 5: Resilience and cost control.
