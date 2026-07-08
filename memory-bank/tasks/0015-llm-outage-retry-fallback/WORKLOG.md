# Worklog — Task 0015

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-08

- Task created from full-code review findings (connection-failure classification verified against `is_transient_error` / `is_quota_exhausted_error`).
- Started implementation: add `is_connection_error` and immediate failover on primary connection outages.
- Added `is_connection_error()` with type-chain and message-marker detection; connection errors are transient and trigger immediate fallback when configured.
- Added 10 regression tests in `tests/test_llm.py`.
- Verification: pytest **149 passed**; eval **16/16**; version **0.13.0**.
- User approved 2026-07-08 — live Ollama-primary CLI verified; task marked **done**.
