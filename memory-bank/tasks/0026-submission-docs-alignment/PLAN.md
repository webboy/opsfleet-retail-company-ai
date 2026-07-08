# Plan — Task 0026

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Review all human-facing docs for unsupported dataset claims and implementation drift.
2. Add a supported-question matrix covering the four expected capability categories.
3. Add schema support explanation, or link to a new `docs/SCHEMA.md` if a separate doc is cleaner.
4. Correct setup/eval/observability wording to match code and CI state after task 0025.
5. Run forbidden-reference checks for `memory-bank`, task IDs, and `.cursor` where required by documentation separation.
6. Verification: docs grep checks plus `python -m retail_agent.evals` if commands changed.
7. Commit(s): likely one `docs: align submission docs with prototype behavior (task 0026)` commit.
