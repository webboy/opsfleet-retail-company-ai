# Plan — Task 0005

1. `safety.py`: `mask_dataframe(df)` (column-name deny-list + content-regex detection) and `mask_text(report)` (email/phone regex sweep). Pure functions, exhaustive unit tests first.
2. Wire `pii_mask` between `execute_bq` and `compose_report`; wire `mask_text` after `compose_report`.
3. `input_guard` node: deterministic pre-filter (SQL keywords like `drop/delete from` in user text, obvious injection phrases) + small LLM classify; route to refuse / reports / analysis.
4. Harden the system prompt (advisory layer).
5. Integration test: fake BQ returns users rows with real-shaped emails/phones → assert masked output end to end.
6. Version minor bump. Commit: `feat(safety): add input guard and deterministic PII masking (task 0005)`.
