# Plan — Task 0009

1. Draft README skeleton (overview → documentation map → setup → run → examples → tests/evals → coverage table → layout).
2. Final pass over `docs/ARCHITECTURE.md` / technical explanation: verify every claim and diagram against the shipped code; fix drift.
3. Write `docs/USAGE.md` (CLI reference, personas editing, adding trios, reading traces/metrics) and `docs/EVALUATION.md` (QA suite workflow + latest results snapshot).
4. Fresh venv dry run of setup steps; fix anything that breaks; capture transcripts for the 4 showcase flows.
5. Write the requirements coverage table (8 rows → code + docs locations); cross-link all documents.
6. Separation audit: grep `README.md` + `docs/` for `memory-bank`, `task 0`, `.cursor` — fix any hits (per `documentation-separation.mdc`).
7. Sweep memory bank (activeContext, progress) and `tasks/INDEX.md` to final state; scan for secrets.
8. Docs-only unless fixes are needed → version bump only if source changed. Commits: `docs: add README with setup, examples and coverage (task 0009)`, `docs: add usage and evaluation guides (task 0009)`.
