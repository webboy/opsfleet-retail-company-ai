# Plan — Task 0025

1. Add GitHub Actions workflow `.github/workflows/ci.yml` — `pytest -q` + dry-run eval on push/PR to `main`.
2. Update `docs/EVALUATION.md` and `README.md` — CI gate section, dry-run vs live honesty, `--live --no-compare` recommendation.
3. Fix stale `tests/test_bq.py` reference and "CI blocks deploy" overclaim in `docs/TECHNICAL_EXPLANATION.md`.
4. No eval-runner behavior change; no version bump (docs/CI only).
5. Verify: `pytest -q`, `python -m retail_agent.evals`.
6. Commit: `ci: add pytest and dry-run eval gate (task 0025)` + docs.
