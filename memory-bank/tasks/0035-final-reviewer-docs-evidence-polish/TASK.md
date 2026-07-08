# Task 0035 — Final reviewer docs and evidence polish

## Metadata

- **Task ID**: 0035
- **Title**: Final reviewer docs and evidence polish
- **Status**: pending_review
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Fix remaining reviewer-facing documentation drift: save flow wording, complete-report gating visibility, assignment capability phrasing, golden retrieval env vars, and optional sanitized live eval evidence.

## Scope

- Human docs only (`README.md`, `docs/*`) plus memory-bank task tracking.
- No version bump (documentation-only).
- Do not mark task 0027 done without explicit user approval.

### Out of scope

- Runtime code changes unless a tiny doc-adjacent fix is strictly necessary.
- Committing eval JSONL artifacts or secrets.

## Acceptance criteria

- [x] Human docs no longer describe automatic “offer to save”; save is user-initiated (`/save` or natural language).
- [x] Complete-report save gating (`last_analysis_complete`) is documented in human docs.
- [x] Assignment phrase “up-to-date revenue by product” appears in reviewer-facing docs where appropriate.
- [x] `GOLDEN_KEYWORD_MIN_OVERLAP` and `GOLDEN_EMBEDDING_MIN_SIMILARITY` are surfaced in Usage/env docs.
- [x] Optional sanitized live eval evidence note added without secrets or noisy JSONL.
- [x] `rg "memory-bank|task 0" README.md docs/` returns no matches.
- [x] `python -m retail_agent.evals` passes.
- [x] Task folder, INDEX, WORKLOG, HANDOFF updated; changes committed.

## References

- Task 0029 — save complete report gating
- Task 0028 / 0034 — golden retrieval thresholds
- Task 0031 / 0032 — prior reviewer docs and live QA evidence
- `docs/ARCHITECTURE.md`, `docs/USAGE.md`, `docs/EVALUATION.md`, `docs/SCHEMA.md`
