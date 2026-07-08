# Progress

## Status snapshot (2026-07-08)

Tasks 0001–0009, **0010**, **0011**, **0012**, **0013**, **0014**, and **0015** **done** (user approved). **0016** polish **pending_review**.

## What works

- Memory bank initialized and task workflow rules in `.cursor/rules/`.
- Production HLD + technical explanation in `docs/` (task 0001, **done**).
- Agent core: LangGraph SQL self-heal + CLI (task 0003, **done**).
- Golden Bucket: trio retrieval, prompt injection, candidate capture (task 0004, **done**).
- Safety: input guard, DataFrame PII mask, output sweep + policy note (task 0005, **done**).
- Saved reports: SQLite store, save/list/delete with interrupt confirmation (task 0006, **done**).
- User preferences + personas: SQLite prefs, deterministic routing, hot-reload persona files (task 0007, **done**).
- LLM provider factory: Gemini, OpenRouter, Ollama with optional fallback (task 0011, **done**).
- Observability: per-node JSONL events, `trace`/`metrics` CLIs (task 0008, **done**).
- QA eval suite: 16 cases, dry-run default, judge scoring, baseline regression (task 0008, **done**).
- **Human docs package**: README, USAGE, EVALUATION, drift-corrected architecture/technical (task 0009, **done**).
- **Optional MCP server**: `retail-agent-mcp`, guarded `query_retail_data` + `retrieve_trios` (task 0010, **done**).
- `pytest` **157 passed**; eval dry-run **16/16 passed**.
- **LLM budget per-turn reset** (task 0013, **done**): `input_guard` uses `fresh_budget`; 6-turn regression test; live CLI verified.
- **CTE support in sql_guard** (task 0012, **done**): bare CTE aliases allowed; 4 regression tests; live BQ verified.
- **Name-flagged PII column masking** (task 0014, **done**): unformatted phones and arbitrary strings masked in PII-named columns; content-detected path unchanged.
- **LLM connection-outage resilience** (task 0015, **done**): connection errors classify as transient; immediate fallback when configured.
- **CLI/docs/eval polish** (task 0016, **pending_review**): analysis-only diagnostics; property-based live eval tokens; docs count drift removed.

## What's left to build

1. ~~`0001`–`0009`, `0011`~~ — **done**
2. ~~`0010` *(optional)* MCP server~~ — **done**
3. ~~`0012` CTE sql_guard~~ — **done**
4. ~~`0014` PII name-flagged masking~~ — **done**
5. ~~`0015` LLM connection resilience~~ — **done**
6. ~~`0016` CLI/docs/eval polish~~ — **pending_review**
7. ~~`0013` LLM budget reset~~ — **done**

## Known issues

- ~~**sql_guard rejects CTE queries**~~ — fixed in task 0012 (**done**).
- ~~**LLM budget not reset per turn**~~ — fixed in task 0013 (**done**).
- ~~**Unformatted phone values leak through name-flagged PII columns**~~ — fixed in task 0014 (**done**).
- ~~**Connection-level LLM outages skip the fallback provider**~~ — fixed in task 0015 (**done**).
- ~~**Stale CLI diagnostics after non-analysis turns; docs test-count drift; brittle live eval token**~~ — fixed in task 0016 (**pending_review**).
- Candidate JSONL grows without automatic pruning — curation workflow documented only.
- Preference phrase detection is deterministic and may miss unusual phrasing.
- Live eval gate requires LLM + BigQuery credentials; dry-run is CI-default.

## Version

- Project version **0.14.0** in `pyproject.toml` and `src/retail_agent/__init__.py` (task 0016 polish).
