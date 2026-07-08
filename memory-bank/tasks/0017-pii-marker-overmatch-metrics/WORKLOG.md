# Worklog — Task 0017

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-08

- Task created from the second deep-review pass. Regression proven end-to-end through the graph: `cancelled_rate`/`email_count` reach the report LLM as `***` with a spurious PII note. Dry-run evals are blind to it (ScriptLLM ignores input) — hence the dry-run-visible guard in acceptance criteria.
- Started implementation: token-boundary PII column matching + numeric metric exemption.
- Implemented `_column_name_tokens()` and token-boundary `_column_is_pii()` in `safety.py`; numeric dtypes skip name-based masking in `mask_dataframe()`.
- Added false-positive/true-positive unit tests in `test_safety.py` and cancelled-rate graph regression in `test_safety_graph.py`.
- Verification: focused safety tests 31 passed; full pytest 167 passed; eval dry-run 16/16.
- Version bumped to **0.15.0**; task set to `pending_review`.
