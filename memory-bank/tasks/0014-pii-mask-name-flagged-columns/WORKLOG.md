# Worklog — Task 0014

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-08

- Task created from full-code review findings (leak reproduced with a `phone` column containing `5551234567`).
- Started implementation: split name-flagged vs content-detected masking in `mask_dataframe`.
- Added `_mask_pii_named_cell_value` for strict name-flagged masking; removed dead `_column_is_pii(text)` branch from `_mask_cell_value`.
- Added regression tests: unformatted phone, arbitrary strings, content-flagged bare digits, numeric columns.
- Verification: pytest **139 passed**; eval **16/16**; sanity `5551234567` → `***-***-4567`; version **0.12.0**.
