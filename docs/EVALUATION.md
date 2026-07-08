# Evaluation Guide

How to run unit tests, the three-layer QA eval suite, LLM-as-judge scoring, and baseline regression checks before deployment.

See also: [README](../README.md), [Usage Guide](./USAGE.md), [Technical Explanation](./TECHNICAL_EXPLANATION.md) (§6 Quality Assurance).

## Quick commands

```bash
# Unit + integration tests (mocked LLM/BQ — no API keys)
pytest -q

# Eval suite — dry-run default (no live credentials)
python -m retail_agent.evals

# Live pre-deploy gate (requires .env + BigQuery ADC)
python -m retail_agent.evals --live

# Safety subset only (baseline comparison is scoped to the selected layer)
python -m retail_agent.evals --layer safety
```

Exit code `0` = all cases passed and no baseline regressions. Exit code `1` = failures or regressions.

## pytest suite

The `tests/` directory covers deterministic logic without live APIs:

- SQL guard (`sql_guard`) — SELECT-only, table whitelist, LIMIT injection
- PII masking — column detection and output regex
- Input guard — injection/off-topic classification
- Graph routing — self-heal retries, delete interrupt, preferences
- Golden retrieval — embedding and keyword fallback
- Eval assertion engine and baseline comparison

```bash
pytest -q                    # quiet summary
pytest tests/test_bq.py -v   # single module
```

Run `pytest -q` for the current passing count; the summary line is the source of truth and is not hard-coded here to avoid documentation drift.

## QA eval suite architecture

Cases are defined in `evals/cases.yaml`. The runner (`python -m retail_agent.evals`) executes each case against the compiled LangGraph agent.

### Three layers

| Layer | Cases | What it checks | Pass criteria |
|-------|-------|----------------|---------------|
| **Capability** | 11 | Revenue, customers, products, time metrics, schema questions | Property assertions on SQL, tables, report content; optional judge score ≥ threshold |
| **Safety** | 5 | Injection, off-topic, PII masking, delete confirmation, destructive SQL | Deterministic pass/fail |
| **Intent (judge)** | Capability only | Does the report answer the question? | LLM scores 1–5 with rationale |

Capability cases use **property assertions**, not exact numeric values — the public BigQuery dataset is rolling and exact figures change over time.

### Dry-run vs live

| Mode | Flag | LLM | BigQuery | Use when |
|------|------|-----|----------|----------|
| **Dry-run** | (default) | `ScriptLLM` with canned SQL/report per case | `FakeBQRunner` with fixture rows | CI, offline verification, regression |
| **Live** | `--live` | Real Gemini (or configured provider) | Real BigQuery | Pre-deploy gate with credentials |

Dry-run is the **default** so reviewers can verify the suite without API keys.

### CLI flags

```bash
python -m retail_agent.evals [options]

  --live              Use live LLM + BigQuery
  --layer {all,capability,safety}
                      Subset of cases (default: all)
  --baseline PATH     Baseline JSONL for regression (default: evals/baseline/dry-run-v0.8.0.jsonl)
  --output PATH       Write this run's results to a JSONL file
  --no-compare        Skip baseline regression check
  --no-judge          Skip LLM-as-judge intent scoring
  --update-baseline   Overwrite baseline with this run (use after intentional behavior change)
```

## LLM-as-judge

For capability cases that pass property assertions, a separate judge prompt (`evals/judge_prompt.md`) scores intent 1–5:

- **Inputs:** user question, generated SQL, result sample, final report
- **Output:** numeric score + short rationale
- **Dry-run:** scripted judge scores from case fixtures
- **Live:** primary Gemini only (no fallback provider) — judge failures are recorded gracefully without aborting the run

Judge runs only on capability layer cases where `judge: true` in `cases.yaml`.

## Baseline and regression workflow

### Stored baseline

`evals/baseline/dry-run-v0.8.0.jsonl` records the v0.8.0 dry-run snapshot:

| Metric | Value |
|--------|-------|
| Total cases | 16 |
| Passed | 16 |
| Failed | 0 |
| Avg judge score (capability) | 4.0 |

Each line records `case_id`, `layer`, `passed`, and `judge_score` (capability only).

### Regression check

By default, `python -m retail_agent.evals` compares the current run against the baseline. A case that **passed before but fails now** is flagged as a regression and causes exit code 1.

When `--layer` is `capability` or `safety`, regression comparison uses only baseline records from that same layer, so subset runs do not report phantom regressions for cases outside the selected layer.

```bash
# Normal CI / pre-commit check
python -m retail_agent.evals

# After intentional behavior change — refresh baseline
python -m retail_agent.evals --update-baseline
```

### Saving run artifacts

```bash
python -m retail_agent.evals --output evals/runs/my-run.jsonl
```

The `evals/runs/` directory is gitignored.

## Example dry-run output

```
Eval summary (dry-run)
  total=16 passed=16 failed=0
  avg_judge_score=4.0
  regressions: none
```

On failure:

```
  FAILED delete-needs-confirm: expected interrupt, got immediate delete
  regressions: delete-needs-confirm (was pass)
```

## Pre-deploy checklist

1. `pytest -q` — all unit tests green
2. `python -m retail_agent.evals` — dry-run passes, no regressions
3. `python -m retail_agent.evals --live` — live gate with real credentials (optional but recommended before demo)
4. Manual spot-check: one manager workflow in `retail-agent --user alice` (analysis → follow-up → preference → save → guarded delete)

## Adding eval cases

1. Add an entry to `evals/cases.yaml` with `id`, `layer`, `question`, `expect` assertions, and optional `dry_run` fixtures for scripted LLM/BQ responses.
2. Run `python -m retail_agent.evals --no-compare` to validate the new case in isolation.
3. If behavior is intentional and stable, update the baseline with `--update-baseline`.

## Related code

| Component | Path |
|-----------|------|
| Case definitions | `evals/cases.yaml` |
| Runner | `src/retail_agent/evals/runner.py` |
| Assertions | `src/retail_agent/evals/assertions.py` |
| Judge | `src/retail_agent/evals/judge.py` |
| Baseline compare | `src/retail_agent/evals/baseline.py` |
| Fake LLM/BQ | `src/retail_agent/evals/fakes.py` |
