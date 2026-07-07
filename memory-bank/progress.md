# Progress

## Status snapshot (2026-07-07)

Tasks 0001–0006 **done** (user approved). Task 0007 **pending_review**. Next: LLM provider fallback (0011), then observability/QA evals (0008).

## What works

- Memory bank initialized and task workflow rules in `.cursor/rules/`.
- Production HLD + technical explanation in `docs/` (task 0001, **done**).
- Agent core: LangGraph SQL self-heal + CLI (task 0003, **done**).
- Golden Bucket: trio retrieval, prompt injection, candidate capture (task 0004, **done**).
- Safety: input guard, DataFrame PII mask, output sweep + policy note (task 0005, **done**).
- Saved reports: SQLite store, save/list/delete with interrupt confirmation (task 0006, **done**).
- User preferences + personas: SQLite prefs, deterministic routing, hot-reload persona files, `/prefs` and `/persona` (task 0007, **pending_review**).
- `pytest` **88 passed**.

## What's left to build

1. ~~`0001` HLD + docs~~ — **done**
2. ~~`0002` Scaffolding + BigQuery~~ — **done**
3. ~~`0003` Agent core~~ — **done**
4. ~~`0004` Golden Bucket~~ — **done**
5. ~~`0005` Safety: input guard + PII masking~~ — **done**
6. ~~`0006` High-Stakes Oversight: saved reports + interrupt-based delete confirmation~~ — **done**
7. `0007` Learning loop: user preferences + personas — **pending_review**
8. `0011` LLM provider fallback: OpenRouter/Ollama (gap from 0003; do before 0008's live evals)
9. `0008` Observability + QA eval suite
10. `0009` Final documentation package and submission polish
11. `0010` *(optional)* MCP server stretch

## Known issues

- `llm.py` is Gemini-only; OpenRouter/Ollama fallback from task 0003 scope not implemented — tracked as task 0011.
- Candidate JSONL grows without automatic pruning — curation workflow documented only.
- Preference phrase detection is deterministic and may miss unusual phrasing.

## Version

- Project version **0.6.0** in `pyproject.toml` and `src/retail_agent/__init__.py` (task 0007).
