# Handoff — Task 0015

## Summary

Extended LLM resilience so connection-level primary outages (refused, DNS, timeout, unreachable) are classified and handled like quota exhaustion when a fallback provider is configured: immediate transparent failover. Without fallback, connection errors retry with backoff up to `max_retries`, then raise for the existing CLI graceful apology path.

## Changed files

- `src/retail_agent/llm.py` — added `is_connection_error()`; updated `is_transient_error()` and `invoke_with_retry()` for immediate connection failover
- `tests/test_llm.py` — classifier, immediate fallback, bounded retry-without-fallback tests
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.13.0**
- `memory-bank/` — task docs, `activeContext.md`, `progress.md`

## Impact

- **Behavior change**: stopped Ollama daemon / network blip on primary no longer skips configured fallback.
- **Unchanged**: quota-exhausted immediate failover; HTTP 5xx transient retry path; per-turn `CallBudget`; eval judge still uses primary-only settings.

## How to verify

1. `pytest tests/test_llm.py -q` — 28 passed
2. `pytest tests/test_graph.py tests/test_safety_graph.py -q` — 13 passed
3. `pytest -q` — 149 passed
4. `python -m retail_agent.evals` — 16/16 dry-run
5. Live (optional): set `RETAIL_AGENT_PROVIDER=ollama`, stop Ollama, configure `RETAIL_AGENT_FALLBACK_PROVIDER=openrouter` — turn should complete via fallback instead of generic CLI apology.

## Risks / rollback

- Immediate failover only triggers for connection-classified errors with fallback configured; prompt/validation errors still fail fast.
- Rollback: revert commit and restore `0.12.0`.

## Acceptance criteria check

- [x] Primary unreachable + working fallback → turn completes via fallback (unit test)
- [x] No fallback → connection failures retry bounded times, then raise gracefully
- [x] `tests/test_llm.py` extended; all existing tests green (149 total)
- [x] Docs wording still matches high-level promise (no update required)
