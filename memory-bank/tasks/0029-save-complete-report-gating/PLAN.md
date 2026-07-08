# Plan — Task 0029

1. Inspect state fields used for `last_analysis_*`, `report_complete`, `status`, and `query_ok`.
2. Update `output_mask` and/or `_save_report` with the narrowest complete-analysis guard.
3. Add regression tests for `/save` after budget exhaustion and fallback.
4. Run targeted report tests, then `pytest -q` and `python -m retail_agent.evals`.
5. Update task docs and mark `Status: done` only if all tests pass per the user's instruction.
