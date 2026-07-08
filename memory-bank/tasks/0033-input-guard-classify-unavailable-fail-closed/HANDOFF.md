# Handoff — Task 0033

## Summary

Fixed classify-unavailable fail-open: when ambiguous input needs LLM guard classification but the classifier cannot run (`BudgetExhaustedError` or quota exhausted), the turn now refuses with `off_topic` instead of entering the analysis pipeline.

## Changed files

- `src/retail_agent/nodes/input_guard.py` — `_classify_unavailable_precheck()` fail-closed helper; budget/quota skip paths use it
- `tests/test_safety_graph.py` — 3 regressions (budget exhausted, quota exhausted, deterministic analysis unchanged)
- `docs/TECHNICAL_EXPLANATION.md` — classifier-unavailable fail-closed wording
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.28.0**

## Verification

```bash
.venv/bin/python -m pytest tests/test_safety.py tests/test_safety_graph.py -q   # 57 passed
.venv/bin/python -m pytest -q                                                    # 235 passed
.venv/bin/python -m retail_agent.evals --layer safety                            # 5/5
.venv/bin/python -m retail_agent.evals                                           # 17/17
```

Manual spot-check: ask an ambiguous question (e.g. *Compare downtown versus suburban trend for leadership*) with `max_llm_calls=0` or exhausted quota — expect polite refusal, no SQL/BQ.

## Acceptance criteria

- [x] Ambiguous budget-exhausted classify → refused `off_topic`
- [x] Ambiguous quota-exhausted classify → refused `off_topic`
- [x] Obvious deterministic analysis unchanged (`Show me recent orders` + zero budget still routes analysis, fails at SQL gen)
- [x] All pytest and eval gates pass
- [x] Version 0.28.0; docs and task metadata updated

## Risks / rollback

- **Residual risk:** Legitimate ambiguous analysis questions are refused when the classifier is unavailable; this is intentional fail-closed safety. Users can rephrase with clearer retail markers to use the deterministic analysis path.
- **Rollback:** Revert `input_guard.py` classify-skip handlers to `precheck.route`; downgrade version if needed.
