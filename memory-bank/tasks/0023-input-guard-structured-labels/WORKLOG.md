# Worklog — Task 0023

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-08

- Created from the strict assignment review. Primary risk: classifier responses containing negated labels can be misrouted because parsing currently uses substring matching.

## 2026-07-08 (implementation)

- Replaced substring-based `parse_llm_guard_label()` with exact first-line / JSON label parsing and `analysis` fallback for ambiguous output.
- Tightened LLM classifier prompt in `input_guard.py` to request one canonical label.
- Added parser regressions for negated/mixed labels and graph tests for ambiguous LLM classification.
- Updated safety docs and bumped version to **0.21.0**.
