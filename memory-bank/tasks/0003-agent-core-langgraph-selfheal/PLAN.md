# Plan — Task 0003

1. `llm.py`: provider factory + retry/backoff + call-budget counter carried in graph state.
2. Define graph state (messages, question, sql, attempts, result, report, budget).
3. Nodes: `generate_sql` → `execute_bq` → conditional edge: ok → `compose_report`; error/empty and attempts < max → `generate_sql` (with error context); else → fallback answer node.
4. Wire checkpointer (in-memory or SQLite) keyed by CLI session thread id.
5. Static schema doc (4 tables, columns, join keys) as prompt asset in `src/retail_agent/assets/schema.md`.
6. `cli.py` REPL (rich rendering, no tracebacks).
7. Tests with fake LLM (scripted responses) and fake BQ runner; assert self-heal transitions and budget cap.
8. Manual smoke against live Gemini + BigQuery; record transcript in WORKLOG.
9. Version: minor bump `0.1.0 → 0.2.0` on completion. Commits: `feat(agent): add LangGraph core with SQL self-heal (task 0003)`, `feat(cli): add chat REPL (task 0003)`.
