# Plan — Task 0004

1. Design trio file format (YAML front-matter + report body); write 8–12 seed trios against `thelook_ecommerce` (validate SQL manually with the runner from 0002).
2. `golden.py`: loader, embedding index (lazy, cached), cosine top-k, keyword-overlap fallback (token Jaccard) on embed failure.
3. Add `retrieve_trios` node + prompt injection into `generate_sql`; store `retrieved_trio_ids` in state.
4. Candidate capture on successful `compose_report` (append-only, no PII — runs after masking once 0005 lands; note ordering in WORKLOG).
5. Tests with fake embedder: ranking, fallback path, capture file contents.
6. Version minor bump. Commit: `feat(golden): add golden bucket trio retrieval and capture (task 0004)`.
