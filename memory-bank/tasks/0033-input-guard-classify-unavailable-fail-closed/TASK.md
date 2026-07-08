# Task 0033 — Input guard classify-unavailable fail-closed

## Metadata

- **Task ID**: 0033
- **Title**: Input guard classify-unavailable fail-closed
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

When ambiguous input requires LLM guard classification but the classifier cannot run (budget exhausted or quota), fail closed to refusal instead of defaulting to the analysis pipeline.

## Scope

- Fix `_llm_classify` classify-skip paths (`BudgetExhaustedError`, quota exhausted) for `needs_llm=True` ambiguous turns.
- Keep deterministic precheck routes unchanged for obvious analysis, schema, chitchat, and report commands.
- Add regression tests for budget and quota classify-skip paths.
- Update reviewer-visible safety docs if wording changes.

### Out of scope

- Changing malformed classifier output handling (task 0030).
- Adding a separate classifier provider or retry policy beyond existing budget/quota handling.

## Acceptance criteria

- [x] Ambiguous `needs_llm=True` input refuses with `off_topic` when guard classify hits `BudgetExhaustedError`.
- [x] Ambiguous input refuses with `off_topic` when guard classify hits quota/exhausted errors.
- [x] Obvious deterministic analysis/schema/chitchat/report routes remain unchanged.
- [x] `pytest tests/test_safety.py tests/test_safety_graph.py -q` pass.
- [x] `pytest -q` pass.
- [x] `python -m retail_agent.evals --layer safety` and full dry-run eval pass.
- [x] Version bumped to 0.28.0; task docs and `INDEX.md` updated; changes committed.

## References

- Final review safety finding: classify-skip reuses `precheck.route` (`analysis`) for ambiguous input.
- Code: `src/retail_agent/nodes/input_guard.py`, `src/retail_agent/safety.py`.
- Related: task 0030 (malformed classifier fail-closed).
