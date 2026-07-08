# Handoff — Task 0023

## Summary

Not started. Task created to harden input guard label parsing.

## Changed files

- TBD

## Impact

- Expected behavior impact: fewer false refusals and safer handling of ambiguous LLM classifier output.
- Expected version impact: minor version bump if versioned source code changes.

## How to verify

1. `pytest -q`
2. `python -m retail_agent.evals --layer safety`
3. Targeted parser regression for negated labels.

## Risks / rollback

- Parser must stay tolerant enough for real LLM responses while avoiding substring ambiguity.

## Acceptance criteria check

- [ ] Pending implementation.
