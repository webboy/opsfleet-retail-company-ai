# Task 0012 — Fix sql_guard: allow CTE (WITH) queries

## Metadata

- **Task ID**: 0012
- **Title**: Fix sql_guard: allow CTE (WITH) queries
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

`sql_guard` currently rejects every query that uses a CTE, because the CTE alias is
treated as a table name and fails the whitelist check. LLMs routinely emit
`WITH ... AS` for analytical questions (monthly trends, per-order aggregates),
so each such query burns the full self-heal loop (3 SQL attempts + LLM calls)
and then falls back — degrading capability and inflating cost.

## Reproduction (confirmed 2026-07-08)

```python
from retail_agent.bq import sql_guard
sql = """WITH monthly AS (
  SELECT DATE_TRUNC(DATE(created_at), MONTH) m, SUM(sale_price) rev
  FROM `bigquery-public-data.thelook_ecommerce.order_items`
  GROUP BY m
)
SELECT * FROM monthly ORDER BY m"""
sql_guard(sql, settings)  # -> ok=False, error="Table not allowed: monthly"
```

Derived-table subqueries (`SELECT ... FROM (SELECT ...) t`) already pass, because
sqlglot models their aliases as subqueries, not `exp.Table` nodes. Only CTE names
leak into `find_all(exp.Table)`.

## Scope

- In `src/retail_agent/bq.py::sql_guard`, collect the set of CTE alias names from
  the parsed expression (`expression.find_all(exp.CTE)`, including nested CTEs)
  and treat bare references to those names as allowed in `_table_allowed`.
- CTE aliases must only be allowed as **bare** names (no project/dataset
  qualifiers); real tables inside CTE bodies must still pass the whitelist.

### Out of scope

- Any relaxation of the SELECT-only / single-statement / whitelist rules.
- Changes to LIMIT injection or bytes-billed capping.

## Acceptance criteria

- [x] A CTE query over allowed tables passes `sql_guard` and executes.
- [x] A CTE whose body references a non-allowed table is still rejected.
- [x] A query referencing a bare non-allowed table name (not a CTE alias) is still rejected.
- [x] Existing `tests/test_sql_guard.py` suite stays green; new tests cover the three cases above.
- [x] Live sanity: `python -m retail_agent.bq "<CTE query>"` returns rows.

## References

- `src/retail_agent/bq.py` (`sql_guard`, `_table_allowed`)
- `tests/test_sql_guard.py`
- Assignment requirement 5 (Resilience — avoid cost inflation) and expected
  capabilities (time-based metrics) in `docs/AI Technical Assignment - Retail Company.pdf`
