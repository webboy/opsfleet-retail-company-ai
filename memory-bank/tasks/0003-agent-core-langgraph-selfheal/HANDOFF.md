# Handoff — Task 0003

## Summary

Delivered the first end-to-end agent core: LangGraph state machine from natural-language question → SQL generation → guarded BigQuery execution → bounded self-heal → analyst report, plus a CLI REPL with conversation memory.

## Changed files

- `src/retail_agent/llm.py`, `deps.py`, `state.py`, `graph.py`, `cli.py`
- `src/retail_agent/schema_doc.py`, `sql_utils.py`, `preview.py`
- `src/retail_agent/assets/schema.md`
- `src/retail_agent/nodes/` — route, schema answer, SQL gen, execute, report, fallback
- `tests/test_graph.py`, `tests/test_llm.py`, `tests/test_sql_utils.py`
- `pyproject.toml`, `requirements.txt`, `__init__.py` (version **0.2.0**)
- Task/memory-bank updates

## Impact

- New CLI entrypoint: `python -m retail_agent.cli --user alice`
- Requires `GOOGLE_API_KEY`, GCP ADC/project for live analytics questions
- Version **0.2.0** (minor bump per task delivery)
- Clear seams left for tasks 0004–0008 (guard, trios, PII, reports, observability nodes)

## How to verify

1. `pip install -e ".[dev]" && pytest -q` — expect 28 passed
2. `python -m retail_agent.cli --user alice`
3. Schema: `What tables and columns do you have?`
4. Analytics: `Who are the top 10 customers by total spend?`
5. Follow-up: `and how about last month?`
6. Self-heal: ask an ambiguous question; check logs for retry attempts and graceful fallback if exhausted

## Risks / rollback

- Live LLM/BQ depend on external APIs and rate limits; call budget defaults to 8/turn, SQL attempts to 3.
- Schema answers use static docs (not live introspection) — sufficient for prototype.
- Rollback: revert task 0003 commit(s).

## Acceptance criteria check

- [x] CLI answers schema + analytics questions — user verified live CLI
- [x] Self-heal on SQL error/empty with max retries then polite fallback — graph tests + routing logic
- [x] LLM call budget + retry/backoff — `llm.py` + unit tests
- [x] Follow-up conversation context — checkpointer + conversation snippet in prompts; graph test
- [x] pytest green with mocked LLM/BQ — 32 passed
- [x] User approval — 2026-07-07
