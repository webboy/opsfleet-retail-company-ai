# Task 0016 — Polish: stale CLI diagnostics, docs test-count drift, brittle live eval assertion

## Metadata

- **Task ID**: 0016
- **Title**: Polish: stale CLI diagnostics, docs test-count drift, brittle live eval assertion
- **Status**: todo
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Bundle of three small, verified issues from the 2026-07-08 full review. None
breaks core behavior, but all are visible to a reviewer.

### A — CLI prints stale diagnostics on non-analysis turns

`sql`, `sql_attempts`, `retrieved_trio_ids` persist in checkpointer state
across turns. After a save/list/prefs turn the CLI re-prints the **previous**
analysis turn's diagnostics. Observed live:

```
You: show my reports
Agent: Your saved reports: ...
[sql attempts=1]                                   <-- stale
[retrieved trios=['monthly-revenue', ...]]         <-- stale
```

The curated README transcript (correctly) shows no such lines after
save/list — code should match. Fix: print `[sql attempts]` /
`[retrieved trios]` only when the finished turn was an analysis turn (e.g.
`result.get("guard_route") == "analysis"`, which `input_guard` rewrites every
turn).

### B — Documentation test-count drift

- `docs/EVALUATION.md`: "the suite contains **120 tests**" — actual `pytest -q`: **132 passed**.
- `memory-bank/progress.md`: "131 passed" — actual 132.

Reword EVALUATION.md so it doesn't hard-code a count that rots (or state the
count with the version it was measured at and refresh it).

### C — Brittle live eval assertion

`evals/cases.yaml` case `top-products-sales` asserts
`report_must_contain: [sold, denim]`. "denim" is a data/model-dependent token;
the live run on 2026-07-08 failed only that assertion (report was otherwise
correct). This contradicts the suite's own property-assertion principle
("dataset is rolling — no exact value assertions"). Relax to data-independent
tokens (e.g. `[sold]` or `[units]`); keep "denim" only in the dry-run judge
fixtures if desired. Also review `revenue-by-traffic-source`'s
`report_must_contain: [search, ...]` for the same brittleness.

## Scope

- `src/retail_agent/cli.py` diagnostics gating (+ test).
- `docs/EVALUATION.md` wording; `memory-bank/progress.md` count.
- `evals/cases.yaml` live-brittle tokens; refresh dry-run baseline only if dry-run results change (they should not).

### Out of scope

- Any graph/state redesign to clear per-turn fields (CLI gating is sufficient here).

## Acceptance criteria

- [ ] Scripted CLI session: no `[sql attempts]` / `[retrieved trios]` lines after save/list/prefs/delete turns; still printed after analysis turns.
- [ ] `docs/EVALUATION.md` no longer states a stale test count; `pytest -q` count matches whatever is claimed.
- [ ] `python -m retail_agent.evals` (dry-run) still 16/16 with no baseline regressions.
- [ ] Live eval capability layer no longer asserts data-dependent product/source tokens.

## References

- `src/retail_agent/cli.py` (report/diagnostics printing)
- `docs/EVALUATION.md`, `memory-bank/progress.md`
- `evals/cases.yaml`, `evals/baseline/dry-run-v0.8.0.jsonl`
- Live eval run 2026-07-08: 14/16 (failures: `top-products-sales` "denim", `cancelled-order-rate` live-model SQL weakness)
