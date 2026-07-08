# Task 0030 — Input guard fail-closed fallback

## Metadata

- **Task ID**: 0030
- **Title**: Input guard fail-closed fallback
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Make ambiguous LLM-assisted guard classification fail closed when the classifier output is malformed or refusal-like.

## Scope

- Change malformed/unknown LLM guard output behavior from permissive `analysis` to safer refusal or one bounded retry.
- Treat explicit refusal-like classifier text as `off_topic` unless a structured valid label is present.
- Update parser and graph tests accordingly.
- Update docs if safety behavior wording changes.

### Out of scope

- Replacing the deterministic precheck.
- Adding a separate classifier provider.

## Acceptance criteria

- [x] Valid structured labels still route correctly.
- [x] Malformed or ambiguous LLM classifier output does not default to analysis.
- [x] Refusal-like text from the classifier is handled safely.
- [x] Safety/unit/graph tests cover the new behavior.
- [x] `pytest -q` and `python -m retail_agent.evals --layer safety` pass.
- [x] Full dry-run eval passes.
- [x] Task metadata, `INDEX.md`, `WORKLOG.md`, and `HANDOFF.md` are updated when complete.

## References

- Final review finding: malformed LLM guard output defaults to `analysis`.
- Code: `src/retail_agent/safety.py`, `src/retail_agent/nodes/input_guard.py`, `tests/test_safety.py`, `tests/test_safety_graph.py`.
