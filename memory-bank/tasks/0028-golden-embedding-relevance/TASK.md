# Task 0028 — Golden embedding relevance

## Metadata

- **Task ID**: 0028
- **Title**: Golden embedding relevance
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Prevent embedding-based Golden Bucket retrieval from injecting irrelevant historical trios into SQL prompts.

## Scope

- Add a relevance threshold or equivalent guard to embedding retrieval.
- Return no trios when best embedding similarity is below the threshold.
- Add regression tests with a fake embedder for unrelated questions.
- Update docs if retrieval policy wording changes.

### Out of scope

- Replacing the embedding provider.
- Building a curation UI.

## Acceptance criteria

- [x] Embedding retrieval does not return arbitrary top-k trios for unrelated questions.
- [x] Relevant questions still retrieve useful trios in tests.
- [x] Keyword zero-overlap behavior remains unchanged.
- [x] `pytest -q` and `python -m retail_agent.evals` pass.
- [x] Task metadata, `INDEX.md`, `WORKLOG.md`, and `HANDOFF.md` are updated when complete.

## References

- Final review finding: embedding retrieval still returns irrelevant trios.
- Code: `src/retail_agent/golden.py`, `tests/test_golden.py`, `tests/test_golden_graph.py`.
