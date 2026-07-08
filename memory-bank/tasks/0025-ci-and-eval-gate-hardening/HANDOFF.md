# Handoff — Task 0025

## Summary

Not started. Task created to add an enforceable QA gate and clarify eval documentation.

## Changed files

- TBD

## Impact

- Expected repo impact: CI or equivalent verification command becomes visible to reviewers.
- Expected version impact: no version bump if docs/CI only; minor bump only if versioned source behavior changes.

## How to verify

1. CI/local gate command runs `pytest -q`.
2. CI/local gate command runs `python -m retail_agent.evals`.
3. `docs/EVALUATION.md` recommends the right live eval command.

## Risks / rollback

- CI must not require live API keys for normal public-repo verification.

## Acceptance criteria check

- [ ] Pending implementation.
