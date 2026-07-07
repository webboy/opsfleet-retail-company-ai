# Progress

## Status snapshot (2026-07-07)

Tasks 0001–0007 **done** (user approved). Task **0011** **pending_review** (LLM provider fallback). Next after approval: observability/QA evals (0008).

## What works

- Memory bank initialized and task workflow rules in `.cursor/rules/`.
- Production HLD + technical explanation in `docs/` (task 0001, **done**).
- Agent core: LangGraph SQL self-heal + CLI (task 0003, **done**).
- Golden Bucket: trio retrieval, prompt injection, candidate capture (task 0004, **done**).
- Safety: input guard, DataFrame PII mask, output sweep + policy note (task 0005, **done**).
- Saved reports: SQLite store, save/list/delete with interrupt confirmation (task 0006, **done**).
- User preferences + personas: SQLite prefs, deterministic routing, hot-reload persona files, `/prefs` and `/persona` (task 0007, **done**).
- LLM provider factory: Gemini, OpenRouter, Ollama with optional fallback on quota/outage (task 0011, **pending_review**).
- `pytest` **98 passed**.

## What's left to build

1. ~~`0001` HLD + docs~~ — **done**
2. ~~`0002` Scaffolding + BigQuery~~ — **done**
3. ~~`0003` Agent core~~ — **done**
4. ~~`0004` Golden Bucket~~ — **done**
5. ~~`0005` Safety: input guard + PII masking~~ — **done**
6. ~~`0006` High-Stakes Oversight: saved reports + interrupt-based delete confirmation~~ — **done**
7. ~~`0007` Learning loop: user preferences + personas~~ — **done**
8. `0011` LLM provider fallback: OpenRouter/Ollama — **pending_review**
9. `0008` Observability + QA eval suite
10. `0009` Final documentation package and submission polish
11. `0010` *(optional)* MCP server stretch

## Known issues

- Candidate JSONL grows without automatic pruning — curation workflow documented only.
- Preference phrase detection is deterministic and may miss unusual phrasing.
- Fallback LLM quality not yet evaluated — task 0008 evals will cover this.

## Version

- Project version **0.7.0** in `pyproject.toml` and `src/retail_agent/__init__.py` (task 0011).
