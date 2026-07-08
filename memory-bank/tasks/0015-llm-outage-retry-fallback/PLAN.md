# Plan — Task 0015

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Add `is_connection_error(exc)` in `llm.py`: check exception type chain (`ConnectionError`, `TimeoutError`, httpx/requests connect errors via class-name match) plus message markers ("connection refused", "connection attempts failed", "name or service not known", "timed out", "unreachable", "connection reset").
2. In `invoke_with_retry`: treat connection errors like quota — immediate failover to fallback when configured; otherwise retry with backoff up to `max_retries`, then raise.
3. Tests: stub primary raising connect-style errors with/without fallback; assert fallback used / graceful raise; assert budget accounting unchanged.
4. Docs: confirm `TECHNICAL_EXPLANATION.md` error-handling table wording matches the implemented behavior ("primary outage → fallback").
5. Commit: `fix(llm): fail over to fallback provider on connection-level outages (task 0015)` + minor version bump.
