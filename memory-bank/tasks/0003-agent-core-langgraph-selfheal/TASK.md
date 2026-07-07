# Task 0003 — Agent core: LangGraph, SQL generation, self-heal, CLI

## Metadata

- **Task ID**: 0003
- **Title**: Agent core: LangGraph, SQL generation, self-heal, CLI
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-07
- **Updated**: 2026-07-07

## Goal

A working end-to-end chat agent: natural-language question → generated SQL → guarded BigQuery execution → self-heal on failure → analyst-style report, via a CLI REPL. This is Requirement 5 (Resilience) plus the backbone for everything else.

## Scope

- `src/retail_agent/llm.py`: model factory (Gemini default, env-configurable), retry/backoff on 429/5xx, per-turn LLM call budget; optional OpenRouter/Ollama fallback provider behind the same interface.
- `src/retail_agent/graph.py` + `src/retail_agent/nodes/`: LangGraph state machine — `generate_sql` (schema-aware prompt), `execute_bq`, `self_heal` (on SQL error or empty result: feed error + previous SQL back to the LLM, max 2 retries, then graceful fallback message), `compose_report`. Conversation memory via checkpointer (thread per CLI session) so follow-up questions work.
- `src/retail_agent/cli.py`: REPL with `--user <id>` flag, renders answers, never shows stack traces; `/exit`, `/help`.
- Table schema description for the 4 tables baked into the prompt context (static, from BigQuery docs/introspection) so the agent can also answer database-structure questions.
- Tests: graph logic with mocked LLM + mocked BQ (self-heal path: fail → retry → succeed; fail ×3 → graceful message); unit tests for llm budget/retry logic.

### Out of scope

- Golden trios (0004), guards/PII (0005), reports library (0006), prefs/personas (0007), observability (0008) — but leave clear seams (node boundaries) for them.

## Acceptance criteria

- [ ] `python -m retail_agent.cli --user alice` answers: top customers, monthly revenue, product performance, and "what tables/columns do you have?".
- [ ] An intentionally hard/ambiguous question triggering bad SQL demonstrates self-heal (visible in logs), and after max retries yields a polite fallback — never a crash.
- [ ] LLM calls per turn are capped; retries use backoff.
- [ ] Follow-up questions use conversation context ("and how about last month?").
- [ ] pytest green with mocked LLM/BQ; result reported in WORKLOG.

## References

- `systemPatterns.md` D1, D2, graph diagram; Requirement 5; LangGraph quickstart links in `techContext.md`.
