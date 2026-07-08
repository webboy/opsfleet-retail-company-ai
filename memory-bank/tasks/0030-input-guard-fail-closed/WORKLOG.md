# Worklog — Task 0030

## 2026-07-08

- Created from final review. Risk: structured parsing fixed substring bugs, but malformed classifier output still falls back to `analysis`.
- Changed `parse_llm_guard_label()` fail-closed fallback from `analysis` to `off_topic` for empty, negated, mixed, malformed, and refusal-like classifier output; valid first-line/JSON labels unchanged.
- Updated unit tests (`test_parse_llm_guard_label_fails_closed_for_negated_or_malformed`) and graph tests (`test_ambiguous_malformed_llm_label_is_refused`, `test_ambiguous_valid_llm_label_still_allows_analysis`).
- Updated `docs/TECHNICAL_EXPLANATION.md` safety wording.
- Bumped version to **0.26.0**.
- Verification: pytest 226 passed; safety eval 5/5; dry-run eval 16/16.
