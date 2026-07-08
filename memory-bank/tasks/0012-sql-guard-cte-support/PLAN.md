# Plan — Task 0012

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. In `sql_guard`, after parsing, build `cte_names = {cte.alias_or_name.lower() for cte in expression.find_all(exp.CTE)}`.
2. Pass `cte_names` into `_table_allowed`; a table with no catalog/db whose name is in `cte_names` is allowed regardless of the whitelist.
3. Tests: add cases to `tests/test_sql_guard.py` — (a) CTE over allowed tables passes; (b) CTE body with disallowed table rejected; (c) bare disallowed table still rejected; (d) nested/multiple CTEs.
4. Docs: no user-facing docs change needed (guard behavior already described generically); mention in WORKLOG.
5. Commit: `fix(bq): allow CTE aliases in sql_guard table whitelist (task 0012)` + minor version bump per `memory-task-minor-version-bump.mdc`.
