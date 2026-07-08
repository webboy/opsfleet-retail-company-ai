# Task 0013 — Fix LLM call budget: reset per turn, not per thread

## Metadata

- **Task ID**: 0013
- **Title**: Fix LLM call budget: reset per turn, not per thread
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

The per-turn LLM call budget (`llm_budget`, default 8 calls) is persisted in
LangGraph checkpointer state and is **never reset** at the start of a new turn.
`input_guard` and `route_turn` both call `resolve_budget(state, deps)`, which
re-loads the accumulated counter. In a single conversation thread the budget is
exhausted after ~4 analysis turns, and every later turn silently degrades to
the "couldn't answer" fallback — breaking the core follow-up-question workflow
and contradicting the documented behavior ("per-turn LLM call budget").

## Reproduction (confirmed 2026-07-08)

Scripted graph run in one thread with mocked LLM/BQ (2 LLM calls per turn):

```
turn 1: status=done      budget={'max_calls': 8, 'used': 2}
turn 4: status=done      budget={'max_calls': 8, 'used': 8}
turn 5: status=fallback  budget={'max_calls': 8, 'used': 8}   <-- bug
turn 6: status=fallback  budget={'max_calls': 8, 'used': 8}
```

## Scope

- Reset the budget to a fresh `CallBudget` at the start of every logical user
  turn. Recommended: `input_guard` uses `fresh_budget(deps)` instead of
  `resolve_budget(state, deps)` (input_guard runs exactly once per turn and is
  not re-entered on interrupt resume; downstream nodes correctly read the
  budget from state).
- Verify interrupt/resume flows (delete confirmation) do not double-reset or
  break — resume re-enters at `reports_router`, which does not use the budget.

### Out of scope

- Changing the budget size or retry policy.
- Cross-turn cost accounting (that belongs in observability, and per-turn
  events already record `llm_budget`).

## Acceptance criteria

- [x] A single-thread conversation of 6+ analysis turns completes with `status=done` on every turn (mocked LLM/BQ regression test).
- [x] Budget still caps calls **within** one turn (existing budget-exhaustion tests stay green).
- [x] Delete-confirmation interrupt/resume flow unaffected (existing tests green).
- [x] Live sanity: multi-question CLI session in one thread keeps answering — covered by regression test; manual CLI optional.

## References

- `src/retail_agent/nodes/input_guard.py`, `src/retail_agent/nodes/route_turn.py`, `src/retail_agent/deps.py` (`resolve_budget`, `fresh_budget`)
- `docs/USAGE.md` ("per-turn LLM call budget (default 8 calls)")
- Assignment requirement 5 (Resilience — no cost inflation, no broken UX)
