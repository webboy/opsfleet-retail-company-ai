# Plan — Task 0027

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Inspect current retrieval fallback and prompt formatting behavior for empty trio lists.
2. Change zero-overlap keyword retrieval to return no trios and ensure observability still records the method/count.
3. Review compose/capture status flow and introduce a minimal complete-report signal if needed.
4. Tests: add unit tests for no-overlap retrieval and graph/node tests for skipped candidate capture on incomplete reports.
5. Docs: update Golden Bucket and learning-loop sections to separate candidate capture from human promotion.
6. Verification: run `pytest -q` and `python -m retail_agent.evals`.
7. Commit(s): likely one `fix(golden): avoid irrelevant trios and incomplete captures (task 0027)` commit with version bump.
