# Handoff — Task 0025

## Summary

Added GitHub Actions CI that runs deterministic verification (`pytest -q` + dry-run eval) on every push/PR to `main`. Human docs now clearly separate CI/dry-run regression gate from optional live smoke tests.

## Changed files

- `.github/workflows/ci.yml` — new CI workflow
- `docs/EVALUATION.md` — CI gate section, dry-run vs live, pre-deploy checklist
- `docs/TECHNICAL_EXPLANATION.md` — accurate CI gate wording
- `README.md` — verification commands aligned with CI
- Memory bank task files and index

## Impact

- Reviewers and contributors see an enforceable offline gate without API keys.
- Live eval documented as optional manual smoke test with `--live --no-compare`.
- No runtime behavior change; version remains **0.22.0**.

## How to verify

1. **Local (same as CI):**
   ```bash
   pip install -e ".[dev]"
   pytest -q
   python -m retail_agent.evals
   ```
2. **Optional live smoke:**
   ```bash
   python -m retail_agent.evals --live --no-compare
   ```
3. Push to GitHub and confirm Actions workflow runs on PR/push to `main`.

## Risks / rollback

- CI does not require secrets; safe for public repo.
- Removing `.github/workflows/ci.yml` reverts the gate.

## User approval

- **2026-07-08**: User confirmed task **0025** done.

## Acceptance criteria check

- [x] CI workflow runs `pytest -q` and `python -m retail_agent.evals`.
- [x] `docs/EVALUATION.md` explains dry-run limits, live usage, baseline, judge behavior.
- [x] Live command documented as `--live --no-compare`.
- [x] Stale paths and overclaims corrected.
- [x] No eval-runner behavior change (no new tests required).
- [x] `pytest -q` and `python -m retail_agent.evals` pass.
