# Plan — Task 0028

1. Read Golden Bucket retrieval code and existing tests.
2. Choose a conservative embedding similarity threshold, configurable only if the existing config pattern makes it cheap.
3. Implement thresholding in `_retrieve_by_embedding`.
4. Add tests for unrelated vs relevant embedding retrieval.
5. Run targeted tests, then `pytest -q` and `python -m retail_agent.evals`.
6. Update task docs and mark `Status: done` only if all tests pass per the user's instruction.
