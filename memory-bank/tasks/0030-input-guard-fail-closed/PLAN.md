# Plan — Task 0030

1. Inspect current guard parser tests and ambiguous-input graph tests.
2. Decide fail-closed behavior: direct `off_topic` fallback unless a better local pattern already exists.
3. Implement parser/prompt updates.
4. Add/update tests for malformed, mixed, refusal-like, and valid structured classifier outputs.
5. Run targeted safety tests, then `pytest -q`, safety eval, and full dry-run eval.
6. Update task docs and mark `Status: done` only if all tests pass per the user's instruction.
