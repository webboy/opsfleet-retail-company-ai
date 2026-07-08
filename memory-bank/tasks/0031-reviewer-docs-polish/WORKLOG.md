# Worklog — Task 0031

## 2026-07-08

- Created from final review. Risk: docs are strong but still have small reviewer-evidence friction in setup and examples.
- Replaced README clone placeholder with discovered remote `https://github.com/webboy/opsfleet-retail-company-ai.git`.
- Aligned README example transcript with shipped CLI: list/delete prompt wording, ISO dates, real `[sql attempts=N]` diagnostics only; removed fabricated `[pii masked…]` and annotated explanatory bracket lines.
- Added guarded-delete variant examples (mention, today, all) in README and `docs/USAGE.md`.
- Labeled `docs/ARCHITECTURE.md` Data flow summary as production HLD with prototype cross-reference.
- Added MIT `LICENSE` file; README license section now points to it.
- Checks: `rg "memory-bank|task 0" README.md docs/` — clean; `python -m retail_agent.evals` — 16/16 passed.
