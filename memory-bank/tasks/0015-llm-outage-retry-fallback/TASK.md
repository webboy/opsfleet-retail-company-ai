# Task 0015 — LLM resilience: retry/fallback on connection-level outages

## Metadata

- **Task ID**: 0015
- **Title**: LLM resilience: retry/fallback on connection-level outages
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Docs (`docs/TECHNICAL_EXPLANATION.md`, `docs/USAGE.md`) promise: "On quota
exhaustion **or primary outage** after retries, the agent transparently retries
on the fallback provider." In code, `invoke_with_retry` only reaches the
fallback for (a) quota-exhausted errors and (b) **transient** errors after max
retries. `is_transient_error` matches HTTP-status markers only — hard outages
such as `Connection refused`, `All connection attempts failed`,
`Name or service not known`, or `timed out` are classified non-transient and
raise immediately: no retry, no fallback, generic CLI apology. Confirmed by
direct classification check on 2026-07-08:

```
'All connection attempts failed'        transient=False quota=False  -> raise
'Connection refused'                    transient=False quota=False  -> raise
'[Errno -2] Name or service not known'  transient=False quota=False  -> raise
'timed out'                             transient=False quota=False  -> raise
```

Practical impact: with `RETAIL_AGENT_PROVIDER=ollama` and a stopped Ollama
daemon (or a network blip on any provider), the configured fallback provider is
never used, contradicting assignment requirement 5 (resilience to third-party
downtime).

## Scope

- Extend `is_transient_error` (or add an `is_connection_error` classifier used
  by `invoke_with_retry`) to cover connection-level failures: refused/reset
  connections, DNS resolution failures, timeouts, unreachable host. Prefer
  matching exception types (`httpx.ConnectError`, `requests.ConnectionError`,
  `TimeoutError`, …) with message markers as a fallback.
- Connection-level failures on the primary should retry with backoff and then
  use the fallback provider, same as transient HTTP errors today.
- Consider failing over to the fallback **immediately** (like quota) for
  connection errors, since retrying a dead endpoint delays the user by the full
  backoff schedule — decide and document in PLAN.

### Out of scope

- Circuit breakers / health checks (documented as production-only).
- Changing the quota-exhausted UX path.

## Acceptance criteria

- [ ] With primary provider unreachable and a working fallback configured, a turn completes via the fallback (unit test with stub models raising `ConnectError`-style exceptions).
- [ ] Without a fallback, connection failures still surface as the graceful CLI apology (no stack trace), after bounded retries.
- [ ] `tests/test_llm.py` extended; existing tests green.
- [ ] Docs updated only if the chosen behavior differs from the current wording.

## References

- `src/retail_agent/llm.py` (`invoke_with_retry`, `is_transient_error`)
- `docs/TECHNICAL_EXPLANATION.md` (Fallback, Error handling table), `docs/USAGE.md` (Provider fallback)
- Assignment requirement 5 (resilient to API/3rd-party failures/downtime)
