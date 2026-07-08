# Worklog — Task 0012

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-08

- Task created from full-code review findings (bug confirmed by direct `sql_guard` reproduction).
- Started implementation: collect CTE aliases via `expression.find_all(exp.CTE)` and allow bare references in `_table_allowed`.
- Implemented `_collect_cte_names` and updated `_table_allowed` in `bq.py`.
- Added 4 CTE tests to `tests/test_sql_guard.py`.
- Verification: pytest **137 passed**; eval **16/16**; live BQ CTE sanity returns 5 rows; version **0.11.0**.
- User approved 2026-07-08.
