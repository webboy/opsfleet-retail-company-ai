# Progress

## Status snapshot (2026-07-08)

Tasks 0001–0008 and **0011** **done** (user approved). Task **0009** **pending_review** (docs package delivered). Optional: **0010** MCP stretch.

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
- **Human docs package**: README, USAGE, EVALUATION, drift-corrected architecture/technical (task 0009, **pending_review**).
- `pytest` **120 passed**; eval dry-run **16/16 passed**.

## What's left to build

1. ~~`0001`–`0008`, `0011`~~ — **done**
2. `0009` Final documentation package — **pending_review** (awaiting user approval)
3. `0010` *(optional)* MCP server stretch

## Known issues

- Candidate JSONL grows without automatic pruning — curation workflow documented only.
- Preference phrase detection is deterministic and may miss unusual phrasing.
- Live eval gate requires Gemini + BigQuery credentials; dry-run is CI-default.

## Version

- Project version **0.8.0** in `pyproject.toml` and `src/retail_agent/__init__.py` (unchanged — task 0009 is docs-only).
