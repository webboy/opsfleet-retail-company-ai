# Task 0024 — Empty results and live eval regression

## Metadata

- **Task ID**: 0024
- **Title**: Empty results and live eval regression
- **Status**: pending_review
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Improve self-heal behavior for valid empty results and close the recorded live eval failure on `cancelled-order-rate`. The agent should self-correct genuine SQL failures without wasting retries on correct zero-row answers.

## Scope

- Change routing/metadata so valid empty query results are treated differently from SQL errors and guard failures.
- Add graph tests for empty-result behavior.
- Investigate the recorded live eval failure in `evals/runs/live-review-2.jsonl` for `cancelled-order-rate`.
- Add a regression test or eval fixture that captures the failing pattern.
- Update user-facing fallback/report language if empty but valid results become reportable.

### Out of scope

- Rebuilding the entire self-heal loop.
- Guaranteeing all live LLM runs pass forever despite model nondeterminism.
- Adding new business capabilities beyond the existing eval suite.

## Acceptance criteria

- [x] Correct empty result sets do not automatically consume all SQL self-heal attempts.
- [x] SQL errors and invalid SQL still retry up to the configured bound.
- [x] `cancelled-order-rate` has a targeted regression test or eval case adjustment based on the live failure root cause.
- [x] Live eval instructions clearly distinguish deterministic dry-run checks from optional live checks.
- [x] `pytest -q` and `python -m retail_agent.evals` pass.
- [ ] If credentials are available, `python -m retail_agent.evals --live --no-compare` is run and the result recorded in `HANDOFF.md`.

## References

- Review finding: legitimate empty query results trigger full self-heal loop.
- Review finding: recorded live eval `cancelled-order-rate` failed with `status expected 'done', got 'fallback'`.
- Code: `src/retail_agent/graph.py`, `src/retail_agent/nodes/execute_bq.py`, `tests/test_graph.py`, `evals/cases.yaml`, `evals/runs/live-review-2.jsonl`.
- Assignment requirements 5 and 6: Resilience and QA.
