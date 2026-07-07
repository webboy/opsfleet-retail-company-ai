# Plan — Task 0006

1. `stores.py`: SQLite schema + CRUD scoped by owner; pure functions, unit tests.
2. `reports_router` node: LLM intent+selector extraction (mentioning X / created today / all mine) → deterministic SQL-side filtering.
3. Delete branch: build candidate list → format for user → `interrupt()` → resume with user reply → strict `yes|confirm` match → delete → report count deleted.
4. Save/list branches + `/save` shortcut in CLI.
5. Tests: two-user isolation, selectors, confirmation transitions (mocked LLM).
6. Version minor bump. Commit: `feat(reports): add saved reports library with guarded deletes (task 0006)`.
