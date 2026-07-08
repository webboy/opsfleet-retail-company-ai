# Handoff — Task 0024

## Summary

Valid empty BigQuery results now route directly to report composition instead of exhausting the SQL self-heal loop. Eval failure records include safe diagnostics for root-cause analysis. Dry-run regressions cover empty-result reporting and cancelled-rate retry recovery.

## Changed files

- `src/retail_agent/graph.py` — route on `query_ok` (including empty results)
- `src/retail_agent/nodes/execute_bq.py` — empty results no longer set `last_error`
- `src/retail_agent/evals/fakes.py` — honor explicit `rows: []`
- `src/retail_agent/evals/runner.py` — failure `diagnostics` in JSONL output
- `tests/test_graph.py` — empty-result and cancelled-rate retry regressions
- `tests/test_eval_fakes.py` — fake spec + diagnostics unit tests
- `docs/TECHNICAL_EXPLANATION.md`, `docs/ARCHITECTURE.md`, `docs/EVALUATION.md`, `docs/USAGE.md`
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.22.0**
- Memory bank task files and index

## Impact

- Valid zero-row queries compose a report on the first attempt (lower LLM/BQ spend, better UX).
- SQL/guard failures still retry up to `max_sql_attempts` (default 3).
- Failed eval JSONL runs now include `diagnostics` with routing/query fields.

## How to verify

1. `pytest -q` — **212 passed**
2. `python -m retail_agent.evals` — **16/16 passed** (dry-run)
3. Optional live check (requires credentials + quota):
   ```bash
   python -m retail_agent.evals --live --no-compare --output evals/runs/my-live-run.jsonl
   ```

## Live eval result (2026-07-08)

Ran `python -m retail_agent.evals --live --no-compare` with credentials available.

| Result | Detail |
|--------|--------|
| Dry-run | 16/16 passed |
| Live | 14/16 passed |
| Still failing live | `cancelled-order-rate`, `product-category-revenue` |

`cancelled-order-rate` live failure diagnostics (new JSONL field):

- `status`: `fallback`
- `sql_attempts`: 3
- `query_ok`: false
- `query_empty`: false
- `last_error`: invalid `GROUP BY total_orders` (aggregation in GROUP BY)
- `retrieved_trio_ids`: includes `cancelled-order-rate`

**Conclusion:** The recorded live regression is caused by live LLM SQL generation errors exhausting retries, not by valid empty results. Task 0024 fixes the empty-result routing bug and adds deterministic regressions; live NL-to-SQL quality for this case remains model-dependent (out of scope per task).

Embedding API hit 429 quota during live run; keyword fallback was used (degraded but functional).

## Risks / rollback

- Empty-result handling intentionally does not retry — a semantically wrong filter that returns zero rows will be reported as “no data” rather than self-healed. This matches the task goal of not wasting retries on correct zero-row answers.

## Acceptance criteria check

- [x] Correct empty result sets do not automatically consume all SQL self-heal attempts.
- [x] SQL errors and invalid SQL still retry up to the configured bound.
- [x] `cancelled-order-rate` has a targeted regression test (retry recovery + metric preservation path in dry-run).
- [x] Live eval instructions clearly distinguish deterministic dry-run checks from optional live checks.
- [x] `pytest -q` and `python -m retail_agent.evals` pass.
- [x] Live eval run attempted and result recorded above (`14/16`; failures documented with diagnostics).
