# Task 0034 — Golden keyword fallback relevance floor

## Metadata

- **Task ID**: 0034
- **Title**: Golden keyword fallback relevance floor
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Prevent keyword-based Golden Bucket fallback from injecting misleading few-shot examples when only a single weak token overlaps between the user question and a stored trio.

## Scope

- Add a conservative keyword relevance floor (minimum overlapping token count).
- Wire through `Settings` when it fits the existing env pattern.
- Regression tests for weak one-token overlap (filtered) and genuine keyword matches (kept).
- Update human docs and `.env.example` if policy or settings change.

### Out of scope

- Replacing Jaccard scoring entirely.
- Embedding retrieval threshold changes (task 0028).

## Acceptance criteria

- [x] No-overlap keyword fallback still returns empty.
- [x] Weak one-token overlap is filtered out.
- [x] Genuinely relevant keyword fallback still retrieves trios in tests.
- [x] `pytest tests/test_golden.py tests/test_golden_graph.py tests/test_mcp_server.py -q`, `pytest -q`, and `python -m retail_agent.evals` pass.
- [x] Task metadata, `INDEX.md`, memory bank, and handoff docs updated; version bumped if source changed.

## References

- Final review finding: `_retrieve_by_keywords` returns trios with any score > 0.
- Prior tasks: 0027 (zero overlap), 0028 (embedding floor).
- Code: `src/retail_agent/golden.py`, `src/retail_agent/config.py`, `tests/test_golden.py`.
