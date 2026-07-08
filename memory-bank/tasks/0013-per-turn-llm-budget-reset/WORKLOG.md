# Worklog — Task 0013

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-08

- Task created from full-code review findings (bug reproduced with a 6-turn scripted graph run in one thread).
- Started implementation: `input_guard` will use `fresh_budget(deps)` at turn start; regression test planned in `tests/test_graph.py`.
- Implemented fix in `input_guard.py` (`fresh_budget` instead of `resolve_budget`).
- Added `test_llm_budget_resets_each_turn_in_same_thread` — 6 turns, one thread, all `done`, `used=2` per turn.
- Verification: pytest **133 passed**; eval dry-run **16/16**; version bumped to **0.10.0**.
- User approved 2026-07-08 — live CLI multi-turn session verified (3+ turns, Ollama fallback after Gemini quota).
