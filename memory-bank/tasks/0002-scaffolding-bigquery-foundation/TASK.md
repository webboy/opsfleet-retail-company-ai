# Task 0002 — Project scaffolding, config & BigQuery foundation

## Metadata

- **Task ID**: 0002
- **Title**: Project scaffolding, config & BigQuery foundation
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-07
- **Updated**: 2026-07-07

## Goal

Create the Python project skeleton and the safe BigQuery access layer everything else builds on.

## Scope

- `pyproject.toml` (project name `retail-agent`, version `0.1.0`, deps per `memory-bank/techContext.md`) + `requirements.txt` mirroring the assignment baseline; `src/retail_agent/` package layout per `systemPatterns.md` component table; `.env.example`; `.gitignore`.
- `src/retail_agent/bq.py`: `BigQueryRunner` (adapt the assignment's `bq_client.py`: execute SQL → pandas DataFrame, logging, error surfaced as typed result) + **`sql_guard`**: single statement, SELECT-only (reject DML/DDL/scripts), only allowed tables (`orders`, `order_items`, `products`, `users` in `bigquery-public-data.thelook_ecommerce`), inject `LIMIT` when missing, set `maximum_bytes_billed`.
- `src/retail_agent/config.py`: env loading (dotenv), settings object.
- pytest setup + unit tests for `sql_guard` (allowed/blocked cases) — no live BigQuery needed for tests.

### Out of scope

- LangGraph graph, LLM calls (task 0003).

## Acceptance criteria

- [ ] `pip install -e .` (or `pip install -r requirements.txt`) works on a clean venv.
- [ ] `sql_guard` blocks: DML/DDL, multi-statement, non-allowed tables; injects LIMIT; unit-tested.
- [ ] `BigQueryRunner` returns DataFrames and typed errors (no raw exceptions leaking); a small manual smoke script/command can run `SELECT 1`-style query against the public dataset when authenticated.
- [ ] Version `0.1.0` set in `pyproject.toml` and `src/retail_agent/__init__.py`.

## References

- Assignment PDF (`bq_client.py`, `requirements.txt` sections); `memory-bank/techContext.md`; `systemPatterns.md` D3.
