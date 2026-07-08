# Task 0025 — CI and eval gate hardening

## Metadata

- **Task ID**: 0025
- **Title**: CI and eval gate hardening
- **Status**: pending_review
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Turn the local QA story into an enforceable and honest gate. Reviewers should see exactly what dry-run evals prove, what live evals prove, and which command would block regressions in CI.

## Scope

- Add a lightweight CI workflow or equivalent repository-level command runner for `pytest -q` and dry-run eval.
- Update eval docs to avoid implying that dry-run canned SQL proves live NL-to-SQL quality.
- Decide whether live eval should default to `--no-compare`, use a live baseline, or document separate live baseline behavior.
- Make judge-unavailable behavior explicit; optionally fail live capability cases when judge scoring is required but unavailable.
- Fix stale documentation references such as `tests/test_bq.py`.

### Out of scope

- Running live eval in public CI without secrets.
- Building a full deployment pipeline.
- Replacing the eval framework.

## Acceptance criteria

- [x] Repository contains a CI workflow or clear local gate script that runs `pytest -q` and `python -m retail_agent.evals`.
- [x] `docs/EVALUATION.md` accurately explains dry-run limitations, live eval usage, baseline comparison, and judge threshold.
- [x] The recommended live command avoids comparing live nondeterministic runs against the dry-run baseline unless intentionally requested.
- [x] Stale test paths and overclaims such as "CI blocks deploy" are corrected.
- [x] Tests cover any eval-runner behavior change.
- [x] `pytest -q` and `python -m retail_agent.evals` pass.

## References

- Review finding: no automated CI gate exists.
- Review finding: dry-run eval proves orchestration, not live SQL generation.
- Review finding: live pre-deploy gate compares against dry-run baseline by default.
- Code/docs: `docs/EVALUATION.md`, `README.md`, `src/retail_agent/evals/`, `.github/workflows/` or equivalent.
- Assignment requirement 6: Quality Assurance.
