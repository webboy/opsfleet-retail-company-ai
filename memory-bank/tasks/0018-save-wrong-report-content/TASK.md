# Task 0018 — /save persists non-analysis output as a "report"

## Metadata

- **Task ID**: 0018
- **Title**: /save persists non-analysis output as a "report"
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

`reports_router._save_report` saves `state.get("report")` — which is simply
the **latest turn's answer text**, whatever kind of turn produced it. If any
non-analysis turn happened between the analysis and `/save`, the library gets
polluted with confirmations, list output, or refusal messages, defeating the
purpose of the Saved Reports feature (requirement 3).

## Reproduction (confirmed 2026-07-08, live CLI and graph-level)

Live session (Ollama): analysis → "I prefer bullet points from now on" →
`/save` stored:

- title: `I prefer bullet points from now on`
- content: `Saved your preference: future reports will use bullets formatting.`

Graph-level scenarios confirmed:

- analysis → preference turn → save ⇒ saves the preference confirmation.
- analysis → "show my reports" → save ⇒ saves "You don't have any saved reports yet."
- analysis → refused off-topic turn → save ⇒ saves the refusal message, titled "write me a poem".

`_latest_analysis_question` already skips report commands when picking the
**title**, but not preference commands or refused questions — and the
**content** is never scoped to analysis at all.

## Scope

- Track the last successful **analysis report** explicitly in graph state
  (e.g. `last_analysis_report` + `last_analysis_question` + `last_analysis_sql`,
  written by `compose_report`/`output_mask` only), and make `_save_report` use
  those fields instead of `report`.
- If no analysis report exists yet in the thread, keep the current "There is
  no recent report to save yet" message — extend it to cover the stale cases.
- Fix `_latest_analysis_question` (or retire it) so titles can't be preference
  phrases or refused questions.

### Out of scope

- Multi-report history/selection ("save the second-to-last report").

## Acceptance criteria

- [x] analysis → preference → `/save` saves the analysis report with the analysis question as title.
- [x] analysis → list → `/save` saves the analysis report.
- [x] refusal-only thread → `/save` responds "no recent report" and saves nothing.
- [x] Existing save/list/delete tests stay green; new graph tests cover the three scenarios.

## References

- `src/retail_agent/nodes/reports_router.py` (`_save_report`, `_latest_analysis_question`)
- `src/retail_agent/state.py`, `src/retail_agent/nodes/compose_report.py`, `nodes/output_mask.py`
- `README.md` ("/save — Save the most recent report"), requirement 3 (High-Stakes Oversight)
