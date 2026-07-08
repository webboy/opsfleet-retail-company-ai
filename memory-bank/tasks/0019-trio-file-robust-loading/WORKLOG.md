# Worklog — Task 0019

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-08

- Task created from the second deep-review pass (CLI startup crash reproduced with a trio file missing the `id` key).
- Started implementation: per-file try/except in `load_trios` with warning logs.
- Implemented skip-and-warn in `load_trios()`; kept strict `load_trio_file()`.
- Added unit tests (3 failure modes + TrioStore startup) and MCP regression test.
- Updated `docs/USAGE.md` with malformed-file skip behavior.
- Verification: golden/MCP tests 17 passed; full pytest 175 passed; eval dry-run 16/16.
- Version bumped to **0.17.0**; task set to `pending_review`.
