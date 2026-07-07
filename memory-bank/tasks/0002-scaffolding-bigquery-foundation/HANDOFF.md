# Handoff — Task 0002

## Summary

Delivered the Python package skeleton and guarded BigQuery foundation: installable `retail-agent` package at version `0.1.0`, environment-backed settings, `sqlglot`-based `sql_guard`, typed `BigQueryRunner`, pytest coverage, and a manual smoke CLI.

## Changed files

- `pyproject.toml`, `requirements.txt`, `.env.example`, `README.md`, `.gitignore` — project metadata and config template
- `src/retail_agent/__init__.py` — package version `0.1.0`
- `src/retail_agent/config.py` — `Settings` + `get_settings()`
- `src/retail_agent/bq.py` — `sql_guard`, `BigQueryRunner`, smoke CLI
- `tests/helpers.py`, `tests/conftest.py`, `tests/test_sql_guard.py`, `tests/test_bq_runner.py` — unit tests
- Task/memory-bank updates (TASK, INDEX, WORKLOG, PLAN, activeContext, progress)

## Impact

- Initial versioned source code at **0.1.0** (first semver baseline; no minor bump beyond initial version).
- Requires: Python 3.11+, `pip install -e ".[dev]"`, GCP ADC for live BigQuery, optional `.env` for `GCP_PROJECT_ID` and future LLM keys.
- New dependency: `sqlglot` for SQL guard parsing.

## How to verify

1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -e ".[dev]"`
3. `pytest -q` — expect 15 passed
4. `gcloud auth application-default login` (if not already)
5. `python -m retail_agent.bq "SELECT order_id, status FROM \`bigquery-public-data.thelook_ecommerce.orders\` LIMIT 5"` — expect 5 rows

## Risks / rollback

- Live BigQuery requires ADC and a billing project; smoke warns if `GCP_PROJECT_ID` unset but can still work via ADC defaults.
- `sql_guard` allows bare table names for the four whitelisted tables — acceptable for prototype; production may require fully qualified names only.
- Rollback: revert the task 0002 commit(s).

## Acceptance criteria check

- [x] `pip install -e .` works on a clean venv — verified with `.venv`
- [x] `sql_guard` blocks DML/DDL, multi-statement, non-allowed tables; injects LIMIT — 11 unit tests
- [x] `BigQueryRunner` returns typed results (no raw exceptions to caller) — mocked + live smoke
- [x] Version `0.1.0` in `pyproject.toml` and `src/retail_agent/__init__.py`
