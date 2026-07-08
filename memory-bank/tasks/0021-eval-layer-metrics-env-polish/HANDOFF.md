# Handoff — Task 0021

**Status:** pending_review

## Summary

Fixed four tooling/observability accuracy issues from the second deep-review pass: eval `--layer` subset runs no longer report phantom baseline regressions; `self_heal_events` counts distinct heal turns instead of per-node events; trace node events suppress stale SQL/trio fields on non-analysis turns; shell environment variables now take precedence over `.env`.

## Changed files

- `src/retail_agent/evals/baseline.py` — `filter_baseline_by_layer()`
- `src/retail_agent/evals/runner.py` — scope baseline comparison to selected layer
- `src/retail_agent/observability.py` — per-turn self-heal metric; analysis-field suppression in snapshots/node events
- `src/retail_agent/config.py` — `load_dotenv(..., override=False)`
- `tests/test_eval_runner.py`, `tests/test_eval_baseline.py`, `tests/test_metrics.py`, `tests/test_observability.py`, `tests/test_config.py` — regressions
- `docs/EVALUATION.md`, `.env.example` — documented layer-scoped baseline and env precedence
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.19.0**
- `memory-bank/tasks/0021-eval-layer-metrics-env-polish/*`, `memory-bank/activeContext.md`, `memory-bank/progress.md`

## Impact

- `python -m retail_agent.evals --layer safety` exits 0 with real safety regressions still detected.
- Metrics CLI reports accurate self-heal turn counts.
- `python -m retail_agent.trace` no longer shows previous-turn SQL/trios on report/list turns.
- Ad-hoc shell overrides (e.g. `RETAIL_AGENT_PERSONA=formal retail-agent ...`) work as expected.

## How to verify

```bash
pytest tests/test_eval_runner.py tests/test_eval_baseline.py tests/test_metrics.py tests/test_observability.py tests/test_config.py -q
pytest -q
python -m retail_agent.evals --layer safety
python -m retail_agent.evals
```

Optional live sanity:

```bash
RETAIL_AGENT_PERSONA=formal retail-agent --user alice
# Expect startup line to show Persona: formal even if .env has default
```

## Risks / rollback

- **Low risk**: observability snapshots omit analysis fields on non-analysis routes by design; raw state in graph checkpoint is unchanged.
- **Rollback**: revert commit; subset evals and env precedence return to prior behavior.

## Acceptance criteria check

- [x] `python -m retail_agent.evals --layer safety` exits 0 with no phantom regressions; full run still catches real regressions.
- [x] `self_heal_events` equals heal turns, not node events; unit test added.
- [x] Trace of save/list turn shows no SQL/trio fields from earlier turns.
- [x] Shell env var beats `.env` for the same variable; monkeypatch + tmp `.env` test added.
- [x] `pytest -q` (189 passed) and dry-run evals green (16/16, safety 5/5).
