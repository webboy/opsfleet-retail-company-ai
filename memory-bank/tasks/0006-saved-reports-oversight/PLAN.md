# Plan — Task 0006

## Policy

- SQLite at `data/reports.sqlite3` (override via `RETAIL_AGENT_DB_PATH`).
- Delete confirmation via LangGraph `interrupt()`; confirm with `yes`, `y`, `confirm`, or `delete`.
- All list/delete operations scoped to `owner = user_id`.

## Steps

1. `stores.py`: owner-scoped CRUD + mention/today/all selectors.
2. Extend `input_guard` with `reports` route; add `reports_router` node with interrupt delete flow.
3. Wire graph: `input_guard -> reports_router | route_turn`.
4. CLI: `/save` shortcut + `Command(resume=...)` on interrupt.
5. Tests for store, ownership, interrupt confirm/cancel.
6. Version `0.5.0`, docs, handoff, commit.
