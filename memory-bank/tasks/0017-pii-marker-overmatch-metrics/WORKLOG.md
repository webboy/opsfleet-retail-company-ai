# Worklog — Task 0017

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-08

- Task created from the second deep-review pass. Regression proven end-to-end through the graph: `cancelled_rate`/`email_count` reach the report LLM as `***` with a spurious PII note. Dry-run evals are blind to it (ScriptLLM ignores input) — hence the dry-run-visible guard in acceptance criteria.
