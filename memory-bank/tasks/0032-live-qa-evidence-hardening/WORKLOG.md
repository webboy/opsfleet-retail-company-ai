# Worklog — Task 0032

## 2026-07-08

- Created from final review. Risk: deterministic gate is strong, but live NL-to-SQL and judge behavior need clearer evidence and tests.
- Inspected eval runner/judge: low scores fail capability cases; judge unavailable returns `None` and passes by default.
- Added `--require-judge` CLI flag and `require_judge` runner parameter for strict live mode when Ollama must score intent.
- Added `valid-empty-result` eval case (17th case) with `query_empty: true` assertion support.
- Added pytest coverage: low judge score, judge unavailable (default vs require), empty-result suite pass, cancelled-order exhaustion diagnostics.
- Documented known live NL-to-SQL limitations and judge behavior in `docs/EVALUATION.md`; updated README and `TECHNICAL_EXPLANATION.md` case counts.
- Version bump **0.27.0**.
- Verification: targeted eval tests 17 passed; full pytest 232 passed; dry-run eval 17/17.
