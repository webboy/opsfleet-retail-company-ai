# Task 0021 — Polish: eval --layer phantom regressions, inflated self-heal metric, stale trace fields, .env precedence

## Metadata

- **Task ID**: 0021
- **Title**: Polish: eval --layer phantom regressions, inflated self-heal metric, stale trace fields, .env precedence
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Four small verified issues from the second deep-review pass. Grouped because
each is low-severity tooling/observability accuracy, not agent behavior.

### A — `--layer` eval subsets fail with phantom regressions

`python -m retail_agent.evals --layer safety` compares the 5-case run against
the **full 16-case baseline**; the 11 capability cases are flagged
"missing from current run" and the run **exits 1** (verified). Yet
`docs/EVALUATION.md` and `--help` advertise `--layer safety` as a normal
invocation. Fix: filter the baseline to the selected layer before comparison
(baseline records already store `layer`), or auto-skip comparison for subset
runs with a printed notice.

### B — `self_heal_events` metric counts node events, not heal turns

`aggregate_metrics` counts every node event with `sql_attempts > 1`. One turn
that retried once emits ~6 such events (generate_sql, execute_bq, pii_mask,
compose_report, output_mask, capture_candidate), inflating the metric ~6x.
Count distinct `turn_id`s with `max(sql_attempts) > 1` instead.

### C — Node events carry stale cross-turn state

Persisted state fields (`sql`, `retrieved_trio_ids`, `sql_attempts`) leak into
node events of later non-analysis turns. Verified: on a "show my reports"
turn, `input_guard` and `reports_router` events carried the **previous**
turn's SQL text and trio IDs, so `python -m retail_agent.trace` shows
misleading lines (same root cause as the CLI wart fixed in task 0016, but at
the observability layer). Fix in `emit_node_event`/`snapshot_state`: only
attach analysis fields when the current turn's `guard_route` is
`analysis`/`schema` (or null them at turn start in the snapshot).

### D — `.env` values override shell environment variables

`_load_env_file` calls `load_dotenv(..., override=True)`, so ad-hoc shell
overrides are silently ignored (verified: `RETAIL_AGENT_PERSONA=formal
retail-agent ...` still uses the `.env` value `default`). Convention is
process env > `.env`. Switch to `override=False` and adjust any tests that
relied on override semantics; document the precedence in `.env.example`.

## Acceptance criteria

- [ ] `python -m retail_agent.evals --layer safety` exits 0 with no phantom regressions; full run still catches real regressions.
- [ ] `self_heal_events` equals the number of turns (not events) with retries; unit test with a two-turn fixture.
- [ ] Trace of a save/list turn shows no SQL/trio fields from earlier turns.
- [ ] Shell env var beats `.env` for the same variable; test via `monkeypatch` + tmp `.env`.
- [ ] `pytest -q` and dry-run evals green.

## References

- `src/retail_agent/evals/runner.py` / `baseline.py` (`compare_runs`), `src/retail_agent/evals/__main__.py`
- `src/retail_agent/observability.py` (`aggregate_metrics`, `snapshot_state`, `emit_node_event`)
- `src/retail_agent/config.py` (`_load_env_file`)
- `docs/EVALUATION.md` (`--layer` flag), task 0016 (CLI-layer counterpart of C)
