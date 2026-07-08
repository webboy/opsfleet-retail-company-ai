# Handoff — Task 0023

## Summary

Hardened LLM-assisted input guard classification by replacing substring label parsing with an exact structured contract. The parser accepts only a first-line canonical label or minimal JSON `{"label": ...}`; negated/mixed/malformed responses fall back to `analysis`.

## Changed files

- `src/retail_agent/safety.py` — `LLM_GUARD_LABELS`, structured `parse_llm_guard_label()`, JSON helper
- `src/retail_agent/nodes/input_guard.py` — stricter classifier prompt
- `tests/test_safety.py` — parser + ambiguous precheck regressions
- `tests/test_safety_graph.py` — ambiguous LLM classify graph regressions
- `docs/TECHNICAL_EXPLANATION.md`, `docs/EVALUATION.md`
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.21.0**

## Impact

- **Behavior:** Responses like `not malicious; analysis` no longer misroute to refusal via substring match.
- **Safety:** Exact `off_topic` / `malicious` labels still refuse before BigQuery.
- **Fallback:** Unknown classifier output defaults to `analysis` for ambiguous turns (same safest intent as before, but without substring false positives).

## How to verify

1. `pytest tests/test_safety.py tests/test_safety_graph.py -q` → **53 passed**
2. `pytest -q` → **207 passed**
3. `python -m retail_agent.evals --layer safety` → **5/5 passed**

## Risks / rollback

- Overly strict parsing could ignore valid prose explanations from the classifier; mitigated by first-line-only acceptance and `analysis` fallback.

## Acceptance criteria check

- [x] All criteria verified during implementation; awaiting user approval for `done`.
