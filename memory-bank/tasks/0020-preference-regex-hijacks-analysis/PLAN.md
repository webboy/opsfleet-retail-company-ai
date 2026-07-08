# Plan — Task 0020

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Rework `_TABLE_PREFERENCE_PATTERNS`: require formatting context ("format", "from now on", "as a table/tables", "in table form", leading "I prefer") and add a negative guard for `\b(?:the\s+)?(?:orders|order_items|products|users|\w+)\s+table\b` DB-reference phrasing.
2. Mirror the audit for bullets/prose patterns.
3. Tests: false-positive matrix (both repro sentences + "which table should I use") and true-positive matrix (existing phrases) in `tests/test_safety.py`.
4. Docs: `docs/USAGE.md` preference examples unchanged; WORKLOG records the tightening.
5. Commit: `fix(safety): require formatting intent in preference detection (task 0020)` + minor version bump.
