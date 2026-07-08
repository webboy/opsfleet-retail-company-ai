# Handoff — Task 0029

## Summary

Gated `/save` so only complete successful analysis reports can be persisted. Incomplete compose output (budget exhaustion), LLM outage messages, and SQL self-heal fallbacks no longer populate or overwrite `last_analysis_*` fields. A prior complete report remains saveable after a later incomplete turn.

## Changed files

- `src/retail_agent/state.py` — added `last_analysis_complete`
- `src/retail_agent/nodes/output_mask.py` — write `last_analysis_*` only on complete analysis
- `src/retail_agent/nodes/reports_router.py` — refuse save when no complete analysis in state
- `tests/test_reports_graph.py` — four regression tests + updated refusal assertion
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.25.0**

## Impact

- Saved report library contains only complete analysis reports.
- Candidate capture behavior from task 0027 unchanged (`report_complete` gate in `capture_candidate`).

## How to verify

1. `pytest tests/test_reports_graph.py tests/test_golden_graph.py -q`
2. `pytest -q`
3. `python -m retail_agent.evals`

## Risks / rollback

- Low risk: valid saves after successful analysis unchanged (existing tests pass).
- Rollback: revert `output_mask`/`reports_router` gating and remove `last_analysis_complete`.

## Acceptance criteria check

- [x] `/save` after incomplete compose output refuses with a clear message.
- [x] `/save` after fallback/error output refuses with a clear message.
- [x] `/save` after a complete analysis still succeeds.
- [x] Candidate capture behavior from task 0027 remains intact.
- [x] `pytest -q` and `python -m retail_agent.evals` pass.
- [x] Task metadata, `INDEX.md`, `WORKLOG.md`, and `HANDOFF.md` updated.
