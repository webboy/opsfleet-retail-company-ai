# Plan — Task 0024

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Reproduce or inspect the `cancelled-order-rate` live failure trace/log to identify whether SQL generation, guard, BigQuery, or retry exhaustion caused fallback.
2. Decide how the graph should represent valid empty results versus recoverable failures.
3. Update graph routing and fallback/report behavior with minimal state changes.
4. Tests: add graph tests for empty-result path and a regression for the cancelled-order-rate failure pattern.
5. Docs: update evaluation/resilience docs if live eval guidance or empty-result behavior changes.
6. Verification: run `pytest -q`, `python -m retail_agent.evals`, and live eval with `--no-compare` when credentials are usable.
7. Commit(s): likely one `fix(graph): handle empty results without exhausting retries (task 0024)` commit with version bump.
