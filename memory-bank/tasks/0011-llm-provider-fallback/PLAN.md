# Plan — Task 0011

1. Study current `llm.py` call sites (`invoke_with_retry`, `create_chat_model` users in nodes/deps) — keep signatures stable.
2. Provider factory: `create_chat_model(provider=...)` for `gemini` / `openrouter` (OpenAI-compatible, `langchain-openai` dep) / `ollama` (`langchain-ollama` dep, optional extra).
3. Wrap invoke path: on quota-exhausted/non-transient primary failure and configured fallback → create fallback model lazily, retry same messages, mark `used_fallback` in result/state; budget shared.
4. Update quota message + `.env.example` + docs alignment.
5. Tests with fake chat models: env selection matrix, fallback trigger, no-fallback unchanged, budget enforcement.
6. Version minor bump. Commit: `feat(llm): add provider factory with OpenRouter/Ollama fallback (task 0011)`.
