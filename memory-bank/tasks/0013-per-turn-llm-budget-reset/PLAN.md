# Plan — Task 0013

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Change `input_guard` to start from `fresh_budget(deps)`; keep writing `llm_budget` into the state update so downstream nodes share the same turn counter.
2. Audit `route_turn` — it may keep `resolve_budget` (it now resolves the fresh value written by `input_guard` in the same turn).
3. Tests: multi-turn regression test in `tests/test_graph.py` (6+ turns, one thread, assert all `done` and `llm_budget.used` resets each turn); keep existing single-turn budget-exhaustion tests.
4. Docs: none needed (behavior matches existing docs after the fix); record in WORKLOG.
5. Commit: `fix(graph): reset LLM call budget at turn start (task 0013)` + minor version bump.
