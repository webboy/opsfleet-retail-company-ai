# Handoff — Task 0035

## Summary

Final reviewer-facing documentation polish: removed “offer to save” drift, documented complete-report save gating, surfaced assignment capability phrasing and golden retrieval env vars, and added a sanitized live eval evidence table. Documentation-only — no version bump.

## Changed files

- `README.md` — assignment capability phrases with link to SCHEMA matrix
- `docs/ARCHITECTURE.md` — user-initiated save in diagram and data-flow step
- `docs/TECHNICAL_EXPLANATION.md` — save gating in §3 High-Stakes Oversight
- `docs/USAGE.md` — saved-reports gating, golden threshold env vars
- `docs/SCHEMA.md` — “up-to-date revenue by product” in supported-question matrix
- `docs/EVALUATION.md` — sanitized live smoke evidence table
- `memory-bank/tasks/0035-final-reviewer-docs-evidence-polish/*`
- `memory-bank/tasks/INDEX.md`, `activeContext.md`, `progress.md`

## Impact

- Documentation only; no runtime or version changes.
- Task **0027** left **pending_review** — no explicit user approval to mark done in this session.

## How to verify

1. `rg "memory-bank|task 0" README.md docs/` — no matches.
2. Skim save sections in USAGE and TECHNICAL §3 — user-initiated save + complete-report gating.
3. Confirm `GOLDEN_EMBEDDING_MIN_SIMILARITY` and `GOLDEN_KEYWORD_MIN_OVERLAP` in USAGE.
4. `.venv/bin/python -m retail_agent.evals` — 17/17 passed.

## Risks / rollback

- Live eval evidence table is a historical snapshot (14/16 on 16-case suite); re-run `--live --no-compare` for current live numbers.
- “Up-to-date revenue by product” maps to existing product/time eval cases — not a separate eval case ID.

## Acceptance criteria check

- [x] No automatic “offer to save” in human docs; save is user-initiated.
- [x] Complete-report save gating documented in USAGE and TECHNICAL §3.
- [x] “Up-to-date revenue by product” in README and SCHEMA matrix.
- [x] Golden retrieval env vars in USAGE.
- [x] Sanitized live eval evidence in EVALUATION (no secrets/JSONL).
- [x] Documentation separation grep clean.
- [x] Dry-run eval 17/17 passed.
- [x] Task metadata, INDEX, WORKLOG, HANDOFF updated.
