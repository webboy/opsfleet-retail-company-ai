# Plan — Task 0034

1. Add `GOLDEN_KEYWORD_MIN_OVERLAP` (default **2**) to `Settings` / `config.py`.
2. Extend `_retrieve_by_keywords` to require at least `min_overlap` shared tokens per trio.
3. Pass settings from `TrioStore.retrieve` into keyword fallback.
4. Tests: weak single-token overlap → empty; existing no-overlap and relevant fallback tests unchanged.
5. Update `docs/ARCHITECTURE.md`, `docs/TECHNICAL_EXPLANATION.md`, `.env.example`.
6. Bump version to **0.29.0**; run pytest + eval; commit and mark task **done**.
