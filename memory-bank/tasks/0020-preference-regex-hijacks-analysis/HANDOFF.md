# Handoff — Task 0020

**Status:** done (user approved 2026-07-08)

## Summary

Tightened deterministic preference detection so database-table analysis questions are no longer routed to `preferences_router` or allowed to overwrite saved output formats. Preference patterns now require explicit formatting intent and skip text that references warehouse tables.

## Changed files

- `src/retail_agent/safety.py` — explicit table/bullet/prose preference patterns; `_references_database_table()` guard
- `tests/test_safety.py` — false-positive and true-positive parametric tests
- `tests/test_preferences_graph.py` — graph regression: table question preserves existing preference
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.18.0**
- `memory-bank/tasks/0020-preference-regex-hijacks-analysis/*` — task docs
- `memory-bank/activeContext.md`, `memory-bank/progress.md`

## Impact

- Questions like `Can I use the orders table to compute revenue?` route to analysis instead of saving `table` format preference.
- Genuine preference phrases (`I prefer tables from now on`, `table format please`, bullet/prose variants, `/prefs`) unchanged.
- Deterministic preference path remains; no LLM added.

## How to verify

```bash
pytest tests/test_safety.py tests/test_preferences_graph.py -q
pytest -q
python -m retail_agent.evals
```

Optional live sanity:

```bash
retail-agent chat --user alice
# Ask: Can I use the orders table to compute revenue?
# Expect an analysis answer, not "Saved your preference..."
```

## Risks / rollback

- **Low risk**: narrower patterns may miss unusual preference phrasing (documented known limitation).
- **Rollback**: revert commit; broad `use ... table` regex returns.

## Acceptance criteria check

- [x] Both reproduction sentences route to analysis and do not touch stored preferences.
- [x] Genuine preference phrases keep working.
- [x] Existing preference tests green; new regression tests added.
