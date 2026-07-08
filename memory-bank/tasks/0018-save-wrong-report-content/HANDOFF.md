# Handoff — Task 0018

## Summary

Fixed `/save` so it persists the last successful **analysis** report instead of whatever text the latest turn wrote to `report`. Graph state now tracks `last_analysis_report`, `last_analysis_question`, and `last_analysis_sql` at the end of the analysis pipeline (`output_mask`).

## Changed files

- `src/retail_agent/state.py` — added `last_analysis_*` fields
- `src/retail_agent/nodes/output_mask.py` — snapshots saveable analysis report after PII sweep
- `src/retail_agent/nodes/reports_router.py` — `_save_report` reads `last_analysis_*`; removed message-history title scan
- `tests/test_reports_graph.py` — three regression tests (preference, list, refusal-only)
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.16.0**
- `memory-bank/tasks/0018-save-wrong-report-content/*` — task docs
- `memory-bank/activeContext.md`, `memory-bank/progress.md`

## Impact

- `/save` after a preference, list, or refusal turn no longer pollutes the Saved Reports library.
- Title and SQL come from the analysis turn, not the intervening non-analysis response.
- No change to list/delete flows or analysis-turn UX.

## How to verify

```bash
pytest tests/test_reports_graph.py -q
pytest -q
python -m retail_agent.evals
```

Optional live sanity:

```bash
retail-agent chat --user alice
# 1. Ask an analytics question
# 2. Say "I prefer bullet points from now on" or "show my reports"
# 3. /save
# 4. "show my reports" — stored content should be the analysis report, not the preference/list reply
```

## Risks / rollback

- **Low risk**: `last_analysis_*` is written only by `output_mask` on the analysis path; other turn types are unaffected.
- **Rollback**: revert commit; `/save` reverts to saving latest `report` (buggy behavior).

## Acceptance criteria check

- [x] analysis → preference → `/save` saves analysis report with analysis question as title.
- [x] analysis → list → `/save` saves analysis report.
- [x] refusal-only thread → `/save` responds "no recent report" and saves nothing.
- [x] Existing save/list/delete tests green; three new graph tests added.
