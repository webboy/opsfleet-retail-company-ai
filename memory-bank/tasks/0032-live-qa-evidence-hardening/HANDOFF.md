# Handoff — Task 0032

## Summary

Hardened live QA evidence: judge low-score and unavailable behavior are now tested; `--require-judge` provides strict live mode; valid empty results have a dedicated eval case; cancelled-order-rate live weakness has deterministic regression evidence and documentation.

## Changed files

- `src/retail_agent/evals/runner.py` — `require_judge` parameter
- `src/retail_agent/evals/__main__.py` — `--require-judge` CLI flag
- `src/retail_agent/evals/assertions.py` — `query_empty: true` assertion
- `evals/cases.yaml` — `valid-empty-result` case
- `evals/baseline/dry-run-v0.8.0.jsonl` — 17-case baseline
- `tests/test_eval_runner.py` — judge and live-weakness regressions
- `tests/test_eval_assertions.py` — empty-result assertion test
- `docs/EVALUATION.md`, `docs/TECHNICAL_EXPLANATION.md`, `README.md`
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.27.0**
- Memory bank task files and index

## Impact

- Dry-run CI remains credential-free and deterministic (17/17).
- Default live eval still warns (not fails) when judge is unavailable; use `--require-judge` for mandatory intent scoring.
- Reviewers have explicit documentation of dry-run vs live proof boundaries and the `cancelled-order-rate` live weakness.

## How to verify

1. `pytest tests/test_eval_judge.py tests/test_eval_runner.py -q` — **17 passed**
2. `pytest -q` — **232 passed**
3. `python -m retail_agent.evals` — **17/17 passed**

Optional strict live check (Ollama required):

```bash
python -m retail_agent.evals --live --no-compare --require-judge
```

## Risks / rollback

- Adding `valid-empty-result` changes baseline total from 16 → 17; intentional re-baseline.
- Live NL-to-SQL quality for complex aggregations remains model-dependent; dry-run green does not imply live green.

## Acceptance criteria check

- [x] Eval runner behavior around judge unavailable/low score is tested.
- [x] Empty-result behavior is represented in eval (`valid-empty-result` case).
- [x] Remaining live limitations are clearly documented for reviewers.
- [x] Dry-run CI gate remains deterministic and credential-free.
- [x] `pytest -q` and `python -m retail_agent.evals` pass.
- [x] Task metadata, `INDEX.md`, `WORKLOG.md`, and `HANDOFF.md` updated.
