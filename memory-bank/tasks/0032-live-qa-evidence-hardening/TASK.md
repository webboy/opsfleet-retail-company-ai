# Task 0032 — Live QA evidence hardening

## Metadata

- **Task ID**: 0032
- **Title**: Live QA evidence hardening
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Reduce false confidence in live QA and make remaining live NL-to-SQL limitations explicit and testable.

## Scope

- Add or improve tests for judge failure/low-score behavior.
- Decide whether live judge unavailable should fail, warn, or require an explicit flag; implement the chosen behavior if appropriate.
- Add an eval or test case for valid empty results if still missing.
- Add a targeted regression or documented evidence path for the `cancelled-order-rate` live weakness.
- Update `docs/EVALUATION.md` and handoff notes with accurate live-vs-dry-run expectations.

### Out of scope

- Requiring live API credentials in default CI.
- Guaranteeing deterministic live LLM output.

## Acceptance criteria

- [x] Eval runner behavior around judge unavailable/low score is tested.
- [x] Empty-result behavior is represented in eval or equivalent regression evidence.
- [x] Remaining live limitations are clearly documented for reviewers.
- [x] Dry-run CI gate remains deterministic and credential-free.
- [x] `pytest -q` and `python -m retail_agent.evals` pass.
- [x] Task metadata, `INDEX.md`, `WORKLOG.md`, and `HANDOFF.md` are updated when complete.

## References

- Final review finding: dry-run eval is green but live NL-to-SQL remains partially proven.
- QA review finding: judge unavailable still passes capability cases.
- Code/docs: `src/retail_agent/evals/runner.py`, `src/retail_agent/evals/judge.py`, `evals/cases.yaml`, `docs/EVALUATION.md`.
