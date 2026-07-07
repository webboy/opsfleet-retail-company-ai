# Plan — Task 0011

## Decisions

- Graph nodes keep calling `invoke_with_retry(llm, messages, budget)`.
- Provider selection + fallback live in `llm.py` via `FallbackChatModel`.
- OpenRouter via `ChatOpenAI` + OpenAI-compatible base URL; Ollama via `ChatOllama`.
- Fallback triggers on quota exhaustion (immediate) or primary failure after retries.

## Steps

1. Extend `config.py` with provider env vars.
2. Refactor `llm.py`: factory + `FallbackChatModel` + invoke fallback path.
3. Add deps, `.env.example`, docs alignment.
4. Offline tests for factory matrix and fallback behavior.
5. Version `0.7.0`, handoff, commit.
