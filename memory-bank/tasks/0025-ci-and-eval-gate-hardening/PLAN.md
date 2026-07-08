# Plan — Task 0025

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Decide the repository's intended CI provider/file format, preferring the simplest public-repo friendly workflow.
2. Add a gate that installs the project and runs `pytest -q` plus dry-run eval.
3. Review eval runner baseline/judge behavior and adjust only where it improves correctness without making local review brittle.
4. Docs: revise `docs/EVALUATION.md`, README verification commands, and any CI/deploy wording.
5. Tests: add/adjust eval-runner tests for any changed baseline or judge behavior.
6. Verification: run `pytest -q` and `python -m retail_agent.evals`.
7. Commit(s): likely one `ci: add pytest and eval gate (task 0025)` plus docs changes, or one combined commit if small.
