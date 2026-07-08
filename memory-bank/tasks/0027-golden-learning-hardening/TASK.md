# Task 0027 — Golden Bucket and learning-loop hardening

## Metadata

- **Task ID**: 0027
- **Title**: Golden Bucket and learning-loop hardening
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Reduce misleading Golden Bucket retrieval and prevent low-quality candidate trios from entering the learning loop. Historical examples should help SQL generation only when relevant, and candidate capture should happen only for complete successful analysis reports.

## Scope

- Change keyword fallback so zero-overlap retrieval returns no trios instead of arbitrary top-k examples.
- Add tests for no-overlap retrieval behavior.
- Decide how embedding calls should interact with per-turn cost controls, or document a separate embedding budget/fallback policy.
- Prevent `capture_candidate` from saving budget-exhaustion or incomplete report outputs as candidate trios.
- Add tests for candidate capture gating.
- Update docs to accurately describe automatic candidate capture and manual analyst curation.

### Out of scope

- Building a full analyst curation UI.
- Replacing local file-based Golden Bucket storage.
- Changing embedding provider/model unless needed for budget behavior.

## Acceptance criteria

- [x] Keyword fallback returns an empty retrieval result when all candidate scores are zero.
- [x] SQL generation prompt handles no retrieved trios cleanly.
- [x] Candidate capture is skipped for budget-exhausted, fallback, or incomplete report states.
- [x] Tests cover zero-overlap retrieval and capture gating.
- [x] Docs distinguish automatic candidate capture from manual promotion into the Golden Bucket.
- [x] `pytest -q` and `python -m retail_agent.evals` pass.

## References

- Review finding: keyword Golden Bucket fallback returns arbitrary trios when there is no overlap.
- Review finding: embedding retrieval is outside per-turn LLM budget.
- Review finding: compose budget exhaustion marks turn `done`, allowing incomplete candidate capture.
- Code: `src/retail_agent/golden.py`, `src/retail_agent/nodes/compose_report.py`, `src/retail_agent/nodes/capture_candidate.py`, `tests/test_golden.py`, `tests/test_golden_graph.py`.
- Assignment requirements 1 and 4: Hybrid Intelligence and Continuous Improvement.
