# Worklog — Task 0028

## 2026-07-08

- Created from final review. Risk: task 0027 fixed keyword zero-overlap only; embedding retrieval still returns top-k without relevance threshold.
- Added `GOLDEN_EMBEDDING_MIN_SIMILARITY` (default **0.35**) to `Settings` and enforced it in `_retrieve_by_embedding`: when best cosine similarity is below the threshold, return no trios; otherwise return top-k matches that meet the threshold.
- Made `FakeEmbedder` use a deterministic token hash (`_stable_token_bucket`) so embedding regression tests are stable across `PYTHONHASHSEED`.
- Tests: unrelated embedding retrieval returns empty; relevant retrieval unchanged; keyword zero-overlap unchanged; MCP shape tests expect only above-threshold trios.
- Docs: `docs/TECHNICAL_EXPLANATION.md`, `docs/ARCHITECTURE.md`, `.env.example` note the embedding similarity floor.
- Version bump **0.23.0 → 0.24.0**.
- Verification: `pytest tests/test_golden.py tests/test_golden_graph.py -q` (18 passed); `pytest -q` (221 passed); `python -m retail_agent.evals` (16/16 dry-run).
