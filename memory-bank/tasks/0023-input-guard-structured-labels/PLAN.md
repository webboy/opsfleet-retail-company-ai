# Plan — Task 0023

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Inspect the current LLM guard prompt and all call sites for `parse_llm_guard_label`.
2. Choose a minimal robust output contract, preferring exact labels with anchored parsing.
3. Implement parser changes and adjust prompt text if necessary.
4. Tests: add parser regression tests for negated/mixed labels and graph tests for ambiguous LLM-classified input.
5. Docs: update safety explanation only if the classifier contract is user/reviewer-visible.
6. Verification: run `pytest -q` and `python -m retail_agent.evals --layer safety`.
7. Commit(s): likely one `fix(safety): parse guard labels exactly (task 0023)` commit with version bump.
