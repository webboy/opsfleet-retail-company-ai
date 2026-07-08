# Task 0010 — Optional: expose guarded capabilities as an MCP server

## Metadata

- **Task ID**: 0010
- **Title**: Optional: expose guarded capabilities as an MCP server
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-07
- **Updated**: 2026-07-08

> **Stretch goal** — start only after tasks 0001–0009 are `pending_review`/`done` and polished, and only if time remains. The core prototype must never depend on this task.

## Goal

Materialize the HLD's MCP extensibility story with a small, working demonstration: a single MCP server exposing the agent's guarded, reusable capabilities so any MCP client (Cursor, Claude, other agents) can use them with the same safety guarantees.

## Scope

- One MCP server (Python SDK, stdio transport) exposing:
  - `query_retail_data(sql)` — runs through the **same** `sql_guard` and `pii_mask` code paths as the agent (safety lives at the server boundary, clients cannot bypass it);
  - `retrieve_trios(question, k)` — read-only Golden Bucket retrieval.
- Reuse existing modules (`bq.py`, `safety.py`, `golden.py`) — no logic duplication; the server is a thin wrapper.
- Strictly additive: CLI agent, tests and evals work identically with or without the server.
- Docs: short human-facing section (`docs/USAGE.md` or `docs/MCP.md`) — how to run it, how to register it in an MCP client, example invocation; update the HLD extensibility section from "design option" to "demonstrated".
- Tests: unit tests for the tool handlers (guard + mask enforced on the server side).

### Out of scope

- Reports library over MCP (stateful, identity-bound — documented as production consideration only); HTTP/SSE transports; auth.

## Acceptance criteria

- [x] MCP server starts and both tools are callable from a real MCP client; a `SELECT` with PII columns returns masked values, DML is rejected — proven from the client side.
- [x] Core prototype behavior unchanged with the server absent (evals pass identically).
- [x] Human docs cover setup/usage; HLD updated.
- [x] pytest green for tool handlers.

## References

- `systemPatterns.md` (extensibility pattern); task 0001 HLD extensibility section; tasks 0002/0004/0005 modules being wrapped.
