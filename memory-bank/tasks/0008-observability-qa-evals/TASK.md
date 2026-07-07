# Task 0008 — Observability & QA evaluation suite

## Metadata

- **Task ID**: 0008
- **Title**: Observability & QA evaluation suite
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-07
- **Updated**: 2026-07-08

## Goal

Requirement 7 (know when and why the agent fails; support deep-dive debugging) and Requirement 6 (evaluate the agent before deployment, verify reports answer user intent).

## Scope

- **Observability** (`src/retail_agent/observability.py`):
  - Structured JSONL event per node execution: turn id, user, node, latency ms, model, SQL text, error class, retry count, guard decision, trios retrieved, PII-mask hit count, tokens where available. Written to `logs/agent_events.jsonl`.
  - `python -m retail_agent.trace <turn_id>`: reconstruct one turn's full message correspondence (deep dive).
  - Metrics summary command (`python -m retail_agent.metrics`): turn success rate, self-heal rate, error classes, guard-block rate, mask hits, p50/p95 latency from the JSONL.
  - Optional LangSmith tracing when `LANGSMITH_*` env vars are set (no hard dependency).
- **QA** (`evals/`) — full suite, three layers (see `systemPatterns.md` D10):
  - **Capability cases** (~15–20 questions across all expected capabilities: customer behavior, product performance, time-based metrics, schema questions) with property-based assertions (expected tables referenced, non-empty result, must-contain / must-not-contain strings — e.g. no raw emails, includes month names).
  - **Safety cases**: injection refused, PII masked end to end, delete requires confirmation, off-topic declined.
  - **Intent-correctness scoring (LLM-as-judge)**: judge prompt receives question + generated SQL + result sample + report, returns 1–5 score with rationale; runner reports aggregate score and flags per-case regressions against a stored baseline run. The rubric scores **decision-usefulness**, not just relevance: (a) does the report answer what the user meant, (b) does it lead with the key insight rather than a data dump, (c) would a manager know what to do/look at next after reading it.
  - Runner `python -m retail_agent.evals` producing a pass/fail + score table; results persisted as JSONL so runs are comparable; documented as the pre-deploy gate.
- Tests: unit tests for the tracer (event shape), metrics aggregation, eval assertion engine and judge-output parsing/regression comparison (with recorded/mocked turns — the judge itself is mocked in tests).

### Out of scope

- Hosted dashboards/alerting (production story in HLD: Cloud Monitoring/LangSmith alerts).

## Acceptance criteria

- [x] Every CLI turn produces JSONL events; `trace` reconstructs a full turn; `metrics` prints the summary.
- [x] Eval runner executes the full suite (capability + safety + judge scoring) in dry-run by default; `--live` for real agent.
- [x] A second eval run compares against the stored baseline and flags regressions.
- [x] pytest green for tracer/metrics/eval engine/judge parsing.

## References

- Requirements 6, 7; `systemPatterns.md` D9, D10; prototype options (d), (e).
