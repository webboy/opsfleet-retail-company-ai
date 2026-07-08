# Handoff — Task 0013

## Summary

Fixed per-turn LLM call budget reset: `input_guard` now starts each logical user turn with `fresh_budget(deps)` instead of reloading accumulated `llm_budget` from checkpointer state. Multi-turn conversations in one thread no longer degrade to fallback after ~4 analysis turns.

## Changed files

- `src/retail_agent/nodes/input_guard.py` — use `fresh_budget(deps)` at turn start
- `tests/test_graph.py` — `test_llm_budget_resets_each_turn_in_same_thread` (6 turns, one thread)
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.10.0**
- `memory-bank/tasks/0013-*/` — task workflow docs

## Impact

- **Version**: 0.9.0 → **0.10.0** (minor bump per task delivery).
- **Behavior**: Each new user turn gets a fresh budget (default 8 LLM calls). Within-turn self-heal retries still share the same turn budget.
- **Unchanged**: `route_turn` still uses `resolve_budget` (reads fresh value from `input_guard`); delete interrupt/resume unaffected.

## How to verify

1. `pytest tests/test_graph.py::test_llm_budget_resets_each_turn_in_same_thread -q`
2. `pytest -q` — expect **133 passed**
3. `python -m retail_agent.evals` — expect **16/16 passed**
4. Live: run 5+ analysis questions in one CLI thread — answers should not stop after turn 4.

## Risks / rollback

- **Risk**: If a future path re-enters `input_guard` mid-turn, budget could reset unexpectedly — current graph does not do this; interrupt resumes at `reports_router`.
- **Rollback**: Revert commit; restore `resolve_budget` in `input_guard`.

## Acceptance criteria check

- [x] 6+ analysis turns in one thread all `status=done` — `test_llm_budget_resets_each_turn_in_same_thread`.
- [x] Within-turn cap preserved — `test_budget_exhaustion_returns_controlled_fallback` green.
- [x] Delete interrupt unaffected — `tests/test_reports_graph.py` green in full suite.
- [x] Multi-turn workflow restored — regression test + existing `test_follow_up_question_keeps_conversation_context`.
