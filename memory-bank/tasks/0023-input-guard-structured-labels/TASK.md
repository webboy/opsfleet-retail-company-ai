# Task 0023 — Input guard structured labels

## Metadata

- **Task ID**: 0023
- **Title**: Input guard structured labels
- **Status**: pending_review
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Make LLM-assisted input classification deterministic and robust. The guard must parse one canonical route label instead of accepting any substring in the model response.

## Scope

- Replace substring-based parsing in `parse_llm_guard_label` with exact first-line, anchored regex, JSON, or other structured parsing.
- Update the guard prompt if needed so model responses are constrained to known labels.
- Add regression tests for negated/mixed responses such as `not off_topic - analysis` and `not malicious; analysis`.
- Revisit the ambiguous-question default path only if needed to make classification safer without increasing false refusals.

### Out of scope

- Replacing the full guard architecture.
- Expanding report-management or preference routing.
- Adding a separate classifier model.

## Acceptance criteria

- [x] LLM guard output must resolve only to one of the allowed labels: `analysis`, `schema`, `chitchat`, `off_topic`, `malicious`.
- [x] Negated labels do not win because of substring ordering.
- [x] Unknown/malformed classifier output falls back to the safest intended default documented in the code/tests.
- [x] Unit tests cover valid labels, mixed/negated labels, and malformed responses.
- [x] Existing safety graph tests and eval safety cases still pass.
- [x] `pytest -q` and `python -m retail_agent.evals --layer safety` pass.

## References

- Review finding: LLM guard label parsing uses brittle substring matching.
- Code: `src/retail_agent/safety.py`, `src/retail_agent/nodes/input_guard.py`, `tests/test_safety.py`, `tests/test_safety_graph.py`.
- Assignment requirement 2: Safety and malicious-user protection.
