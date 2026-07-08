# Plan — Task 0016

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. CLI: gate diagnostic prints on `result.get("guard_route") == "analysis"` (set fresh by `input_guard` every turn); add a REPL-level test or graph-state assertion covering a save/list turn following an analysis turn.
2. Docs: reword `docs/EVALUATION.md` pytest section (drop hard-coded 120 or re-measure); sync `memory-bank/progress.md`.
3. Evals: replace `denim` (and audit `search`) in `report_must_contain` with data-independent tokens; run dry-run suite; update baseline only if strictly necessary.
4. Tests: `pytest -q` and `python -m retail_agent.evals` both green.
5. Commit: `fix(cli): suppress stale SQL diagnostics on non-analysis turns (task 0016)` + `docs(evals): remove stale counts and brittle live assertions (task 0016)`; minor version bump (CLI code changed).
