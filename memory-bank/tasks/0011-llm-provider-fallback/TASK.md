# Task 0011 — LLM provider fallback: OpenRouter / Ollama

## Metadata

- **Task ID**: 0011
- **Title**: LLM provider fallback: OpenRouter / Ollama
- **Status**: todo
- **Owner**: Engineer
- **Created**: 2026-07-07
- **Updated**: 2026-07-07

## Goal

Close the gap left by task 0003: the assignment (Requirement 5, resilience to third-party downtime) and `systemPatterns.md` D2 call for an **optional OpenRouter/Ollama fallback provider behind the same interface** as Gemini. Today `llm.py` supports only `ChatGoogleGenerativeAI`; when the Gemini free-tier daily quota is exhausted the agent has no LLM at all.

## Scope

- Extend `src/retail_agent/llm.py` into a proper **provider factory**:
  - `RETAIL_AGENT_PROVIDER` env (default `gemini`; options `openrouter`, `ollama`) selecting the primary provider;
  - `RETAIL_AGENT_FALLBACK_PROVIDER` env (optional) — on non-transient provider failure (quota exhausted, outage after retries), transparently retry the call on the fallback provider within the same turn budget;
  - OpenRouter via OpenAI-compatible endpoint (`OPENROUTER_API_KEY`, `RETAIL_AGENT_OPENROUTER_MODEL`); Ollama via `OLLAMA_HOST` + `RETAIL_AGENT_OLLAMA_MODEL` (reference: Opsfleet `lc-openrouter-ollama-client`);
  - all providers return LangChain `BaseChatModel` — graph nodes stay untouched.
- Fallback events recorded in state/logs (observability seam for task 0008).
- Quota-exhausted user message updated to mention the configured fallback (or how to enable one).
- `.env.example` updated; human docs updated (`docs/TECHNICAL_EXPLANATION.md` fallback section already describes this — align reality with docs; setup notes for OpenRouter/Ollama go to README/USAGE in task 0009 if not earlier).
- Tests: factory selection per env; fallback trigger on quota error (fake providers); budget still enforced across fallback calls.

### Out of scope

- Embedding-model fallback (keyword fallback already exists in `golden.py`); model routing/load balancing.

## Acceptance criteria

- [ ] With `RETAIL_AGENT_PROVIDER=openrouter` (valid key) the CLI answers questions with no Gemini key at all.
- [ ] With Gemini primary + OpenRouter fallback configured, a simulated quota-exhausted error transparently completes the turn via fallback (visible in logs).
- [ ] With no fallback configured, behavior is unchanged (current graceful quota message).
- [ ] pytest green for factory + fallback logic (fake providers, no live calls).

## References

- Requirement 5 (API/3rd-party resilience); `systemPatterns.md` D2; `techContext.md` env table; task 0003 scope (unimplemented item); https://github.com/Opsfleet/lc-openrouter-ollama-client
