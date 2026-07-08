# Plan — Task 0035

1. Add task folder and INDEX row (`todo` → `in_progress` → `pending_review`).
2. Fix “offer to save” drift in `docs/ARCHITECTURE.md` (diagram + data-flow step).
3. Document user-initiated save and complete-report gating in `docs/USAGE.md` and `docs/TECHNICAL_EXPLANATION.md` §3.
4. Surface assignment capability phrase in `README.md` and `docs/SCHEMA.md` supported-question matrix.
5. Add `GOLDEN_EMBEDDING_MIN_SIMILARITY` and `GOLDEN_KEYWORD_MIN_OVERLAP` to `docs/USAGE.md` environment section.
6. Add sanitized live eval evidence summary to `docs/EVALUATION.md` (no JSONL commits).
7. Run forbidden-reference grep, `python -m retail_agent.evals`, update memory-bank context, commit.
