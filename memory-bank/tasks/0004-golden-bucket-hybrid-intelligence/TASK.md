# Task 0004 — Hybrid Intelligence: Golden Bucket trio retrieval

## Metadata

- **Task ID**: 0004
- **Title**: Hybrid Intelligence: Golden Bucket trio retrieval
- **Status**: todo
- **Owner**: Engineer
- **Created**: 2026-07-07
- **Updated**: 2026-07-07

## Goal

Ground SQL generation in expert knowledge: retrieve the most relevant historical Trios (Question → SQL → Analyst Report) at query time and inject them into the generation prompt (Requirement 1).

## Scope

- `golden_bucket/` folder with ~8–12 handcrafted seed trios as individual files (YAML or Markdown with front-matter: question, sql, report excerpt, tags) covering the expected capabilities (top customers, monthly revenue, product performance, branch comparison style questions, schema questions).
- `src/retail_agent/golden.py`: load trios; embed questions (Gemini embeddings) with in-memory index; `retrieve(question, k=3)`; **keyword-overlap fallback** when the embedding API is unavailable (resilience).
- New graph node `retrieve_trios` before `generate_sql`; retrieved trios injected as few-shot examples; retrieval result recorded in state (for observability later).
- **Candidate capture** (system-level learning seam): successful turns append question+SQL+report to `golden_bucket/candidates/` (or JSONL) for future analyst curation — the promotion pipeline itself is documented in `docs/` (task 0001), not built.
- Tests: retrieval ranking with a fake embedder; keyword fallback; candidate capture writes.

### Out of scope

- Vector DB / GCS production implementation (documented in HLD only); analyst review UI.

## Acceptance criteria

- [ ] Asking a question similar to a seed trio demonstrably pulls that trio into the prompt (log/trace shows it) and improves the generated SQL shape.
- [ ] Embedding API failure degrades to keyword retrieval, not to a crash.
- [ ] Successful turns produce candidate trio records.
- [ ] pytest green for retrieval, fallback, capture.

## References

- Requirement 1; `systemPatterns.md` D4, D7 (system learning).
