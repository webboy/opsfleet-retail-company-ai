# Evaluation Guide

How to run unit tests, the three-layer QA eval suite, LLM-as-judge scoring, and baseline regression checks before deployment.

See also: [README](../README.md), [Usage Guide](./USAGE.md), [Technical Explanation](./TECHNICAL_EXPLANATION.md) (§6 Quality Assurance).

## Quick commands

```bash
# Unit + integration tests (mocked LLM/BQ — no API keys)
pytest -q

# Eval suite — dry-run default (no live credentials)
python -m retail_agent.evals

# Live pre-deploy check (requires .env + BigQuery ADC; do not compare to dry-run baseline)
python -m retail_agent.evals --live --no-compare

# Safety subset only (baseline comparison is scoped to the selected layer)
python -m retail_agent.evals --layer safety
```

Exit code `0` = all cases passed and no baseline regressions (dry-run default). Exit code `1` = failures or regressions.

## CI gate (deterministic, no API keys)

GitHub Actions workflow [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs on pushes and pull requests to `main`:

1. `pip install -e ".[dev]"`
2. `pytest -q`
3. `python -m retail_agent.evals`

This is the **enforceable regression gate** for the public repo. It proves unit/integration coverage and dry-run eval orchestration against the committed baseline. It does **not** run live LLM or BigQuery.

Run the same checks locally before opening a PR:

```bash
pip install -e ".[dev]"
pytest -q
python -m retail_agent.evals
```

## pytest suite

The `tests/` directory covers deterministic logic without live APIs:

- SQL guard (`sql_guard`) — SELECT-only, table whitelist, LIMIT injection/clamping
- PII masking — column detection and output regex
- Input guard — injection/off-topic classification with exact structured LLM label parsing
- Graph routing — self-heal retries on SQL/guard failures, empty-result reporting, delete interrupt, preferences
- Golden retrieval — embedding and keyword fallback
- Eval assertion engine and baseline comparison

```bash
pytest -q                              # quiet summary
pytest tests/test_sql_guard.py -v      # single module
```

Run `pytest -q` for the current passing count; the summary line is the source of truth and is not hard-coded here to avoid documentation drift.

## QA eval suite architecture

Cases are defined in `evals/cases.yaml`. The runner (`python -m retail_agent.evals`) executes each case against the compiled LangGraph agent.

### Three layers

| Layer | Cases | What it checks | Pass criteria |
|-------|-------|----------------|---------------|
| **Capability** | 12 | Revenue, customers, products, time metrics, valid empty results, [schema questions](./SCHEMA.md) | Property assertions on SQL, tables, report content; judge score ≥ 3 when judge runs |
| **Safety** | 5 | Injection, off-topic, PII masking, delete confirmation, destructive SQL | Deterministic pass/fail |
| **Intent (judge)** | Capability only | Does the report answer the question? | LLM scores 1–5 with rationale; **score &lt; 3 fails** the case |

Capability cases use **property assertions**, not exact numeric values — the public BigQuery dataset is rolling and exact figures change over time.

### Dry-run vs live

| Mode | Flag | LLM | BigQuery | Use when |
|------|------|-----|----------|----------|
| **Dry-run** | (default) | `ScriptLLM` with canned SQL/report per case | `FakeBQRunner` with fixture rows | CI, offline verification, regression |
| **Live** | `--live` | Configured agent provider (e.g. Ollama/Gemini) | Real BigQuery | Optional pre-demo smoke test with credentials |

Dry-run is the **default** and the **CI gate**. It is deterministic: scripted LLM/BQ fixtures replay the same outcomes on every run. It validates graph routing, safety guards, property assertions, and baseline regression — **not** live natural-language-to-SQL quality.

Live mode (`--live`) is optional for manual pre-demo checks with real credentials. **Always use `--no-compare`** for live runs unless you intentionally maintain a separate live baseline; comparing live nondeterministic output against the dry-run baseline will produce false regressions. Failed cases in saved JSONL runs include a `diagnostics` object with `status`, `sql`, `sql_attempts`, `last_error`, `query_ok`, `query_empty`, and `retrieved_trio_ids`.

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
  --require-judge     Fail capability cases when judge scoring is unavailable (strict live mode)
  --update-baseline   Overwrite baseline with this run (use after intentional behavior change)
```

## LLM-as-judge

For capability cases that pass property assertions, a separate judge prompt (`evals/judge_prompt.md`) scores intent 1–5:

- **Inputs:** user question, generated SQL, result sample, final report
- **Output:** numeric score + short rationale
- **Dry-run:** scripted judge scores from case fixtures
- **Live:** local **Ollama** only (`RETAIL_AGENT_OLLAMA_MODEL`, `OLLAMA_HOST`) — no cloud fallback, so judge scoring does not consume Gemini quota

Judge runs only on capability layer cases where `judge: true` in `cases.yaml`. The `schema-tables` case skips judge scoring (`judge: false`) because it validates the [schema route](./SCHEMA.md#schema-question-route), not SQL quality.

**Judge unavailable (default):** If live judge scoring is unavailable (e.g. Ollama not running), the case records `judge unavailable` in the rationale and **does not fail** the run — only a **score below 3** fails a passing case. This keeps optional live smoke tests usable when the judge service is down.

**Strict mode:** Pass `--require-judge` with `--live` when you want capability cases to **fail** if judge scoring cannot run. Dry-run CI does not use this flag; scripted judge scores from case fixtures always satisfy the judge step.

## Baseline and regression workflow

### Stored baseline

`evals/baseline/dry-run-v0.8.0.jsonl` records a **historical** dry-run snapshot from package v0.8.0. The filename is kept for regression continuity — it is **not** tied to the current package version. Re-baseline with `--update-baseline` after intentional behavior changes.

| Metric | Value |
|--------|-------|
| Total cases | 17 |
| Passed | 17 |
| Failed | 0 |
| Avg judge score (capability) | 4.0 |

Each line records `case_id`, `layer`, `passed`, and `judge_score` (capability only). Failed runs may also include a `diagnostics` object with safe query/routing fields for root-cause analysis.

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
  total=17 passed=17 failed=0
  avg_judge_score=4.0
  regressions: none
```

On failure:

```
  FAILED delete-needs-confirm: expected interrupt, got immediate delete
  regressions: delete-needs-confirm (was pass)
```

## Pre-deploy checklist

1. **CI / local gate** — `pytest -q` and `python -m retail_agent.evals` (same as GitHub Actions; no API keys)
2. **Optional live smoke test** — `python -m retail_agent.evals --live --no-compare` with credentials (validates real LLM + BigQuery; results vary by model/quota). Add `--require-judge` when Ollama is running and you want intent scoring to be mandatory.
3. Manual spot-check: one manager workflow in `retail-agent --user alice` (analysis → follow-up → preference → save → guarded delete)

## Known live NL-to-SQL limitations

Dry-run eval proves graph routing, safety, and property assertions with scripted fixtures. It does **not** prove that a live LLM will generate correct SQL on the first try.

Documented live weakness (reproduced 2026-07-08 with Ollama-primary):

| Case | Dry-run | Typical live issue |
|------|---------|-------------------|
| `cancelled-order-rate` | Passes (scripted SQL) | Live LLM may emit invalid aggregation SQL (e.g. `GROUP BY total_orders`), exhaust 3 self-heal attempts, and fall back |

Deterministic regression evidence (no credentials):

- `tests/test_graph.py::test_cancelled_rate_recovers_after_failed_sql_attempt` — retry recovery path
- `tests/test_eval_runner.py::test_cancelled_order_rate_exhaustion_matches_live_failure_pattern` — exhaustion fallback with live-like diagnostics (`sql_attempts=3`, `query_ok=false`, trio `cancelled-order-rate` retrieved)

Failed live runs include `diagnostics` in saved JSONL (`status`, `sql`, `sql_attempts`, `last_error`, `query_ok`, `query_empty`, `retrieved_trio_ids`) for root-cause analysis.

## Recorded live smoke evidence (sanitized)

Optional live runs require credentials and vary by model/quota. The table below summarizes one **sanitized manual run** (2026-07-08, Ollama-primary, `--live --no-compare`) — no secrets, no committed JSONL artifacts. Re-run locally for current numbers after model or case changes.

| Gate | Result | Notes |
|------|--------|-------|
| Dry-run CI (`python -m retail_agent.evals`) | **17/17 passed** | Deterministic; committed baseline |
| Live smoke (same date, 16-case suite then) | **14/16 passed** | Failures: `cancelled-order-rate` (SQL self-heal exhausted), `product-category-revenue` (live NL-to-SQL) |
| Known live weakness today | `cancelled-order-rate` | Documented above; dry-run + unit tests cover routing |
| Embedding API | 429 during run | Keyword fallback used (`method=keyword` in diagnostics) |

The suite now has **17** cases (added `valid-empty-result` in a later release). Live pass rates are not CI-enforced — use dry-run for regression gates and live for optional pre-demo smoke only.

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
