# Handoff — Task 0027

## Summary

Not started. Task created to harden Golden Bucket retrieval and candidate capture quality.

## Changed files

- TBD

## Impact

- Expected behavior impact: fewer irrelevant few-shot examples and cleaner candidate-trio queue.
- Expected version impact: minor version bump if versioned source code changes.

## How to verify

1. `pytest -q`
2. `python -m retail_agent.evals`
3. Targeted retrieval/capture tests for no-overlap and incomplete-report cases.

## Risks / rollback

- Returning no trios on weak matches must not reduce useful grounding for common retail questions.

## Acceptance criteria check

- [ ] Pending implementation.
