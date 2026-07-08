# Progress

## Status snapshot (2026-07-08)

Tasks 0001–0009 and **0011** **done** (user approved). **0010** MCP stretch **pending_review**. Bug-fix tasks **0012–0016** created from the full-code review — all **todo**.

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
- **Optional MCP server**: `retail-agent-mcp`, guarded `query_retail_data` + `retrieve_trios` (task 0010, **pending_review**).
- `pytest` **132 passed**; eval dry-run **16/16 passed**; live eval (Ollama) **14/16** on 2026-07-08 (failures documented in task 0016).

## What's left to build

1. ~~`0001`–`0009`, `0011`~~ — **done**
2. `0010` *(optional)* MCP server — **pending_review** (awaiting user approval)
3. `0012`–`0016` bug fixes from the 2026-07-08 full review — **todo** (see `tasks/INDEX.md`)

## Known issues

- **sql_guard rejects CTE queries** (task 0012) — CTE alias treated as disallowed table.
- **LLM budget not reset per turn** (task 0013) — long single-thread conversations degrade to fallback.
- **Unformatted phone values leak through name-flagged PII columns** (task 0014).
- **Connection-level LLM outages skip the fallback provider** (task 0015).
- **Stale CLI diagnostics after non-analysis turns; docs test-count drift; brittle live eval token** (task 0016).
- Candidate JSONL grows without automatic pruning — curation workflow documented only.
- Preference phrase detection is deterministic and may miss unusual phrasing.
- Live eval gate requires LLM + BigQuery credentials; dry-run is CI-default.

## Version

- Project version **0.9.0** in `pyproject.toml` and `src/retail_agent/__init__.py` (task 0010 MCP delivery).
