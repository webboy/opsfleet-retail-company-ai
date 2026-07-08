# Plan — Task 0032

1. Inspect eval runner/judge tests and current live documentation.
2. Add low-score and judge-unavailable test coverage.
3. Add empty-result eval evidence or equivalent regression if missing.
4. Improve live eval docs without making CI depend on secrets.
5. Run targeted eval tests, then `pytest -q` and `python -m retail_agent.evals`.
6. Update task docs and mark `Status: done` only if all tests pass per the user's instruction.
