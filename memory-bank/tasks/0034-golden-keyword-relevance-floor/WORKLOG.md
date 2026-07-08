# Worklog — Task 0034

## 2026-07-08

- Created task from final review finding: keyword fallback accepts any Jaccard score > 0, allowing weak one-token overlap.
- Added `GOLDEN_KEYWORD_MIN_OVERLAP` (default **2**) to `Settings`.
- `_retrieve_by_keywords` now sorts by overlap count then Jaccard score; filters trios below the floor.
- Test `test_keyword_fallback_filters_weak_single_token_overlap` — only "monthly" shared → empty.
- Updated human docs and `.env.example`; version **0.29.0**.
- pytest **236 passed**; dry-run eval **17/17 passed**.
