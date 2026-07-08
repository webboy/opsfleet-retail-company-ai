# Task 0029 — Save complete report gating

## Metadata

- **Task ID**: 0029
- **Title**: Save complete report gating
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Ensure `/save` can persist only complete successful analysis reports, never budget-exhaustion stubs, LLM outage messages, or fallback text.

## Scope

- Prevent `output_mask` from updating last-analysis fields for incomplete or fallback reports.
- Gate `_save_report` on complete successful analysis state.
- Add graph regression tests for budget exhaustion/fallback followed by `/save`.
- Keep valid `/save` behavior for successful analysis unchanged.

### Out of scope

- Redesigning saved report storage.
- Changing delete confirmation behavior.

## Acceptance criteria

- [x] `/save` after incomplete compose output refuses with a clear message.
- [x] `/save` after fallback/error output refuses with a clear message.
- [x] `/save` after a complete analysis still succeeds.
- [x] Candidate capture behavior from task 0027 remains intact.
- [x] `pytest -q` and `python -m retail_agent.evals` pass.
- [x] Task metadata, `INDEX.md`, `WORKLOG.md`, and `HANDOFF.md` are updated when complete.

## References

- Final review finding: `/save` can persist incomplete or error stub reports.
- Code: `src/retail_agent/nodes/output_mask.py`, `src/retail_agent/nodes/reports_router.py`, `tests/test_reports_graph.py`, `tests/test_golden_graph.py`.
