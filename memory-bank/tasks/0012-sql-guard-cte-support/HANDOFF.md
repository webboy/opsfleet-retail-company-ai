# Handoff — Task 0012

## Summary

Fixed `sql_guard` to allow bare CTE (`WITH`) alias references while preserving physical table whitelist enforcement. CTE names are collected from `expression.find_all(exp.CTE)` and permitted only as unqualified table references; real tables inside CTE bodies still pass the same whitelist checks.

## Changed files

- `src/retail_agent/bq.py` — `_collect_cte_names`, `_table_allowed` CTE alias support
- `tests/test_sql_guard.py` — 4 new CTE regression tests
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.11.0**
- `memory-bank/tasks/0012-*/` — task workflow docs

## Impact

- **Version**: 0.10.0 → **0.11.0** (minor bump per task delivery).
- **Behavior**: `WITH monthly AS (...) SELECT * FROM monthly` now passes guard when CTE body uses allowed tables.
- **Unchanged**: SELECT-only, single-statement, DML/DDL block, physical table whitelist, LIMIT injection, bytes billed.

## How to verify

1. `pytest tests/test_sql_guard.py -q` — expect **16 passed**
2. `pytest -q` — expect **137 passed**
3. `python -m retail_agent.evals` — expect **16/16 passed**
4. Live:
   ```bash
   python -m retail_agent.bq "WITH monthly AS (SELECT DATE_TRUNC(DATE(created_at), MONTH) AS m, SUM(sale_price) AS rev FROM \`bigquery-public-data.thelook_ecommerce.order_items\` GROUP BY m) SELECT * FROM monthly ORDER BY m LIMIT 5"
   ```

## Risks / rollback

- **Risk**: A CTE alias that collides with an allowed bare table name could mask a real table reference — unlikely in practice; LLMs use distinct CTE names.
- **Rollback**: Revert commit; CTE queries fail guard again.

## Acceptance criteria check

- [x] CTE over allowed tables passes and executes — unit + live BQ sanity.
- [x] CTE body with disallowed table rejected — `test_cte_body_with_disallowed_table_is_blocked`.
- [x] Bare non-CTE disallowed table rejected — `test_bare_disallowed_non_cte_table_still_blocked`.
- [x] Existing suite green + new tests — 16 sql_guard tests, 137 total pytest.
- [x] Live CTE returns rows — verified.
