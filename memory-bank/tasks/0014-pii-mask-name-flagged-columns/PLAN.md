# Plan — Task 0014

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Split `mask_dataframe` per-column handling: `name_flagged = _column_is_pii(column)`; if name-flagged use a strict cell masker (never returns the original value); else keep the current shape-based masker for content-flagged columns.
2. Strict masker: email shape → `_mask_email_value`; ≥7-digit value → `_mask_phone_value`; otherwise `"***"`.
3. Drop the `_column_is_pii(text)` branch from `_mask_cell_value`.
4. Tests: unformatted phone column fully masked; mixed-content contact column fully masked; content-flagged detection unchanged; numeric columns untouched.
5. Docs: `docs/TECHNICAL_EXPLANATION.md` §2 already describes name-based masking as unconditional — code catches up to docs; note in WORKLOG.
6. Commit: `fix(safety): unconditionally mask name-flagged PII columns (task 0014)` + minor version bump.
