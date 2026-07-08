# Progress

## Status snapshot (2026-07-08)

Tasks 0001–0009, **0010**, **0011**, **0012**, **0013**, **0014**, **0015**, **0016**, and **0017** **done** (user approved). Second deep-review pass tasks **0018–0021**: **0018** is **pending_review**, **0019–0021** remain **todo**.

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
- `pytest` **170 passed**; eval dry-run **16/16 passed**.
- **LLM budget per-turn reset** (task 0013, **done**): `input_guard` uses `fresh_budget`; 6-turn regression test; live CLI verified.
- **CTE support in sql_guard** (task 0012, **done**): bare CTE aliases allowed; 4 regression tests; live BQ verified.
- **Name-flagged PII column masking** (task 0014, **done**): unformatted phones and arbitrary strings masked in PII-named columns; content-detected path unchanged.
- **LLM connection-outage resilience** (task 0015, **done**): connection errors classify as transient; immediate fallback when configured.
- **CLI/docs/eval polish** (task 0016, **done**): analysis-only diagnostics; property-based live eval tokens; docs count drift removed.
- **PII marker token matching** (task 0017, **done**): metric columns like `cancelled_rate`/`email_count` no longer falsely masked; string PII columns still strictly masked.
- **Save last analysis report** (task 0018, **pending_review**): `/save` uses `last_analysis_*` instead of latest turn answer.

## What's left to build

1. ~~`0001`–`0009`, `0011`~~ — **done**
2. ~~`0010` *(optional)* MCP server~~ — **done**
3. ~~`0012` CTE sql_guard~~ — **done**
4. ~~`0014` PII name-flagged masking~~ — **done**
5. ~~`0015` LLM connection resilience~~ — **done**
6. ~~`0016` CLI/docs/eval polish~~ — **done**
7. ~~`0013` LLM budget reset~~ — **done**
8. ~~`0017` PII marker over-match~~ — **done**
9. `0018` `/save` scope fix — **pending_review**
10. `0019`–`0021` bug fixes from the 2026-07-08 second review pass — **todo** (see `tasks/INDEX.md`)

## Known issues

- ~~**sql_guard rejects CTE queries**~~ — fixed in task 0012 (**done**).
- ~~**LLM budget not reset per turn**~~ — fixed in task 0013 (**done**).
- ~~**Unformatted phone values leak through name-flagged PII columns**~~ — fixed in task 0014 (**done**).
- ~~**Connection-level LLM outages skip the fallback provider**~~ — fixed in task 0015 (**done**).
- ~~**Stale CLI diagnostics after non-analysis turns; docs test-count drift; brittle live eval token**~~ — fixed in task 0016 (**done**).
- ~~**PII markers over-match**~~ — fixed in task 0017 (**done**).
- ~~**/save persists non-analysis output**~~ — fixed in task 0018 (**pending_review**): `last_analysis_*` state fields.
- **Malformed trio file crashes CLI startup** (task 0019, **todo**) — raw traceback; loader should skip-and-warn.
- **Preference regex hijacks analysis questions** (task 0020, **todo**) — "use the orders table…" silently rewrites saved preferences.
- **Tooling polish** (task 0021, **todo**) — eval `--layer` phantom regressions (exit 1); `self_heal_events` ~6x inflated; stale SQL/trios in node events; `.env` overrides shell env.
- Candidate JSONL grows without automatic pruning — curation workflow documented only.
- Preference phrase detection is deterministic and may miss unusual phrasing.
- Live eval gate requires LLM + BigQuery credentials; dry-run is CI-default.
- llama3.2 (local) SQL quality: complex questions (e.g. cancelled-order share) can exhaust 3 self-heal attempts; Gemini fallback or a larger local model handles them.

## Version

- Project version **0.16.0** in `pyproject.toml` and `src/retail_agent/__init__.py` (task 0018 save scope fix).
