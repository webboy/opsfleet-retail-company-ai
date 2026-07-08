# Worklog — Task 0029

## 2026-07-08

- Created from final review. Risk: `capture_candidate` uses `report_complete`, but saved reports still rely only on `last_analysis_report` existence.
- Inspected state: `report_complete` set in `compose_report`; `output_mask` was unconditionally writing `last_analysis_*` for all compose paths including budget-exhaustion stubs.
- Gated `output_mask` to update `last_analysis_*` and `last_analysis_complete` only when `report_complete`, `status=done`, and `query_ok`.
- Gated `_save_report` on `last_analysis_complete` with a clear refusal message for incomplete/fallback turns.
- Added `last_analysis_complete` to `AgentState`.
- Added graph regression tests: budget exhaustion, self-heal fallback, compose LLM outage, and prior-complete-report preservation.
- Version bump **0.25.0**.
- Verification: pytest 225 passed; dry-run eval 16/16 passed.
