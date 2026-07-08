# Worklog — Task 0020

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-08

- Task created from the second deep-review pass (both reproduction sentences verified against `classify_input_precheck` and `parse_preference_command`).
- Started implementation: require formatting intent and skip DB-table references in preference detection.
- Replaced broad table/bullet/prose regexes with explicit formatting-intent patterns; added `_references_database_table()`.
- Added safety parametric tests and graph regression for preference preservation.
- Verification: safety/prefs tests 40 passed; full pytest 183 passed; eval dry-run 16/16.
- Version bumped to **0.18.0**; task set to `pending_review`.
