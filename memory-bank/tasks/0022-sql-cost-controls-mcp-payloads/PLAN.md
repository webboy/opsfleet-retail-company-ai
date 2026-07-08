# Plan — Task 0022

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Inspect current settings and SQL guard tests to decide whether to reuse `default_limit` as the hard cap or introduce a separate response/query cap.
2. Update `sql_guard` so explicit `LIMIT` values above the cap are reduced deterministically.
3. Update MCP query handler to cap serialized rows and expose truncation metadata.
4. Tests: add/extend unit tests for SQL limit clamping and MCP payload truncation.
5. Docs: update `README.md`, `docs/TECHNICAL_EXPLANATION.md`, and/or `docs/MCP.md` where guardrails are described.
6. Verification: run `pytest -q` and `python -m retail_agent.evals`.
7. Commit(s): likely one `fix(bq): clamp query limits and MCP row payloads (task 0022)` commit with version bump.
