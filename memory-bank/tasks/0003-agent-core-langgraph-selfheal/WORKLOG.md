# Worklog — Task 0003

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-07

- Task started (`in_progress`); synced `0002` to `done` in TASK/INDEX.
- Added `llm.py` (Gemini factory, retry/backoff, per-turn `CallBudget`), `schema_doc.py`, `assets/schema.md`.
- Added LangGraph core: `state.py`, `deps.py`, `graph.py`, nodes (`route_turn`, `answer_schema`, `generate_sql`, `execute_bq`, `compose_report`, `fallback_answer`), helpers (`sql_utils.py`, `preview.py`).
- Added `cli.py` REPL with `--user`, `/help`, `/exit`, in-memory checkpointer for follow-ups.
- Tests: 12 new cases (graph self-heal paths, schema routing, budget, LLM retry) — **28 passed** total.
- Live smoke: schema question via graph returned structured table/column answer (Gemini + static schema).
- Post-review fix: greetings (`Helo`) route to chitchat reply; `sql_guard` catches sqlglot `TokenError` on non-SQL LLM output.
- User approved CLI manually (2026-07-07). Task marked **done**.
