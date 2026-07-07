# Plan — Task 0008

## Confirmed decisions

- `python -m retail_agent.evals` defaults to dry-run/fake mode; live runs require `--live`.
- Intent judge uses the existing provider factory/settings with a separate judge prompt.
- Commit a small dry-run baseline; live eval outputs stay gitignored under `evals/runs/`.
- Trace records safe summaries only (no full result rows or prompt dumps).

## Steps

1. `observability.py`: `TurnTracer`, safe JSONL events, metrics/trace helpers.
2. `deps.tracer` + traced node wrapper in `graph.py`; CLI `turn_id` lifecycle.
3. `trace.py` and `metrics.py` CLI modules.
4. `evals/cases.yaml`, `evals/judge_prompt.md`, `src/retail_agent/evals/*` runner/assertions/judge/baseline.
5. pytest for tracer, metrics, trace, eval engine, judge parsing, baseline diff, dry-run runner.
6. Human docs + memory bank; version **0.8.0**; `pending_review`; commit.
