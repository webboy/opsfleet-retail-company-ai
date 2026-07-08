# Handoff — Task 0030

## Summary

Ambiguous LLM guard classification now fails closed: malformed, negated, mixed, empty, or refusal-like classifier output routes to `off_topic` instead of permissive `analysis`. Valid structured first-line and JSON labels are unchanged.

## Changed files

- `src/retail_agent/safety.py` — `parse_llm_guard_label()` fail-closed to `off_topic`
- `tests/test_safety.py` — updated parser fallback expectations
- `tests/test_safety_graph.py` — malformed-label refusal + valid-label allowance graph tests
- `docs/TECHNICAL_EXPLANATION.md` — input guard safety wording
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.26.0**

## Impact

- Ambiguous questions that reach the LLM classifier are refused when the model does not return a structured label, preventing accidental pipeline entry on classifier failures.
- Legitimate ambiguous retail questions still work when the classifier returns a valid `analysis` label.

## How to verify

1. `pytest tests/test_safety.py tests/test_safety_graph.py -q` → 54 passed
2. `pytest -q` → 226 passed
3. `python -m retail_agent.evals --layer safety` → 5/5
4. `python -m retail_agent.evals` → 16/16 dry-run

## Risks / rollback

- Fail-closed behavior may refuse some legitimate ambiguous questions when the classifier returns prose instead of a label; users can rephrase with clearer retail analytics wording.
- Rollback: revert `parse_llm_guard_label()` fallback to `analysis`.

## Acceptance criteria check

- [x] Valid structured labels still route correctly.
- [x] Malformed or ambiguous LLM classifier output does not default to analysis.
- [x] Refusal-like text from the classifier is handled safely (`off_topic`).
- [x] Safety/unit/graph tests cover the new behavior.
- [x] `pytest -q` and `python -m retail_agent.evals --layer safety` pass.
- [x] Full dry-run eval passes.
- [x] Task metadata, `INDEX.md`, `WORKLOG.md`, and `HANDOFF.md` updated.
