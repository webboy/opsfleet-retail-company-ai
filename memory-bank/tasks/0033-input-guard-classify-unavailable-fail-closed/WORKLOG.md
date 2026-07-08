# Worklog — Task 0033

## 2026-07-08

- Created task folder and added INDEX row (todo → in_progress → done).
- Inspected `input_guard._llm_classify`: `BudgetExhaustedError` and quota paths reused `precheck.route` (`analysis` for ambiguous input).
- Added `_classify_unavailable_precheck()` returning refused `off_topic` when `needs_llm=True`.
- Added graph regressions: budget exhausted, quota exhausted, deterministic analysis unchanged.
- Updated `docs/TECHNICAL_EXPLANATION.md` for classifier-unavailable fail-closed.
- Bumped version to **0.28.0**.
- Tests: pytest 235 passed; safety eval 5/5; dry-run eval 17/17.
