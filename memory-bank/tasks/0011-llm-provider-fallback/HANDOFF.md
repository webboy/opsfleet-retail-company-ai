# Handoff — Task 0011

## Summary

Implemented a configurable LLM provider factory (Gemini, OpenRouter, Ollama) with optional fallback on quota exhaustion or primary outage after retries. Graph nodes remain unchanged — they still call `invoke_with_retry(llm, messages, budget)`.

## Changed files

- `src/retail_agent/config.py` — provider/fallback/OpenRouter/Ollama settings
- `src/retail_agent/llm.py` — factory, `FallbackChatModel`, fallback in `invoke_with_retry`, quota message updates
- `src/retail_agent/cli.py` — quota message uses provider/fallback settings
- `pyproject.toml` — `langchain-openai`, `langchain-ollama`; version **0.7.0**
- `src/retail_agent/__init__.py` — version **0.7.0**
- `.env.example` — provider/fallback env documentation
- `docs/TECHNICAL_EXPLANATION.md` — aligned fallback architecture with implementation
- `tests/test_llm.py`, `tests/helpers.py` — offline factory and fallback tests

## Impact

- **Env**: new optional vars — `RETAIL_AGENT_PROVIDER`, `RETAIL_AGENT_FALLBACK_PROVIDER`, `OPENROUTER_API_KEY`, `RETAIL_AGENT_OPENROUTER_MODEL`, `OLLAMA_HOST`, `RETAIL_AGENT_OLLAMA_MODEL`.
- **Behavior**: default unchanged (Gemini only). With fallback configured, quota/outage on primary retries on fallback within the same per-turn LLM budget.
- **Version**: **0.7.0** (minor bump per task delivery).

## How to verify

1. `pytest -q` — expect **98 passed** (no live LLM calls).
2. **Gemini only** (existing `.env`): no change required.
3. **OpenRouter primary**:
   ```bash
   export RETAIL_AGENT_PROVIDER=openrouter
   export OPENROUTER_API_KEY=...
   export RETAIL_AGENT_OPENROUTER_MODEL=...
   retail-agent
   ```
   Ask a data question — should work without `GOOGLE_API_KEY`.
4. **Gemini + OpenRouter fallback**:
   ```bash
   export RETAIL_AGENT_PROVIDER=gemini
   export RETAIL_AGENT_FALLBACK_PROVIDER=openrouter
   export OPENROUTER_API_KEY=...
   export RETAIL_AGENT_OPENROUTER_MODEL=...
   ```
   When Gemini quota is exhausted, the turn should complete via OpenRouter instead of stopping with only the quota message.

## Risks / rollback

- OpenRouter/Ollama model quality may differ from Gemini — SQL generation quality not guaranteed on fallback.
- Rollback: remove fallback env vars or revert to pre-0011 `llm.py`; set `RETAIL_AGENT_PROVIDER=gemini` only.

## Acceptance criteria check

- [x] OpenRouter primary without Gemini key — factory tests + manual smoke above.
- [x] Gemini primary + OpenRouter fallback on simulated quota — `test_fallback_triggers_on_quota_exhausted`.
- [x] No fallback preserves graceful quota behavior — `test_no_fallback_preserves_quota_error`.
- [x] pytest green — **98 passed**.
