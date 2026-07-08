# Plan — Task 0021

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. A: in `run_suite`, pass the selected layer into the baseline comparison and filter `baseline` records by `layer` (records already persist it); add a runner test for `--layer safety` with the default baseline.
2. B: rework `aggregate_metrics` self-heal counting to per-turn `max(sql_attempts)`; unit test.
3. C: in `snapshot_state`/`emit_node_event`, suppress `sql`, `sql_attempts`, `retrieved_trio_ids`, `retrieval_method` when the turn's `guard_route` is not analysis/schema; adjust trace tests.
4. D: `load_dotenv(env_path, override=False)`; verify no test depended on override; document precedence in `.env.example` comment.
5. Docs: `docs/EVALUATION.md` — one line on baseline scoping for subset runs.
6. Commits: split A+B+C (`fix(obs/evals)`) and D (`fix(config)`), Conventional Commits, task 0021 referenced; minor version bump with the code change.
