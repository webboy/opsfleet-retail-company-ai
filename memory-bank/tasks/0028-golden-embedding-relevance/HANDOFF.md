# Handoff — Task 0028

## Summary

Embedding-based Golden Bucket retrieval now applies a cosine-similarity floor (`GOLDEN_EMBEDDING_MIN_SIMILARITY`, default **0.35**). Unrelated questions no longer inject arbitrary top-k trios into SQL prompts; relevant questions still retrieve matching examples. Keyword zero-overlap fallback is unchanged.

## Changed files

- `src/retail_agent/golden.py` — similarity threshold in `_retrieve_by_embedding`; deterministic `FakeEmbedder` token hashing
- `src/retail_agent/config.py` — `embedding_min_similarity` setting + `GOLDEN_EMBEDDING_MIN_SIMILARITY` env
- `src/retail_agent/__init__.py`, `pyproject.toml` — version **0.24.0**
- `tests/test_golden.py`, `tests/test_golden_graph.py` — embedding relevance regressions
- `tests/test_mcp_server.py` — expect only above-threshold trios
- `tests/helpers.py`, eval/judge test Settings stubs — new setting field
- `docs/TECHNICAL_EXPLANATION.md`, `docs/ARCHITECTURE.md`, `.env.example` — retrieval policy wording

## Impact

- SQL generation prompts receive fewer irrelevant few-shot examples when the user question is off-topic for all seed trios.
- Override threshold via `GOLDEN_EMBEDDING_MIN_SIMILARITY` if tuning for a larger golden bucket.

## How to verify

1. `pytest tests/test_golden.py tests/test_golden_graph.py -q`
2. `pytest -q`
3. `python -m retail_agent.evals`

## Risks / rollback

- Threshold **0.35** is conservative for the prototype seed bucket; a much larger bucket with near-duplicate phrasing may need a lower value via env.
- Real Gemini embedding scores differ from `FakeEmbedder`; monitor live retrieval if trios seem under-retrieved.

## Acceptance criteria check

- [x] Embedding retrieval does not return arbitrary top-k trios for unrelated questions
- [x] Relevant questions still retrieve useful trios in tests
- [x] Keyword zero-overlap behavior remains unchanged
- [x] `pytest -q` and `python -m retail_agent.evals` pass
- [x] Task metadata, `INDEX.md`, `WORKLOG.md`, and `HANDOFF.md` updated
