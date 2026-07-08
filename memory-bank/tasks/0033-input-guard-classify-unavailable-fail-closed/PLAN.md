# Plan — Task 0033

1. Reproduce: ambiguous question + `max_llm_calls=0` or quota error currently routes to analysis.
2. Change `_llm_classify` classify-skip handlers to return refused `off_topic` when `precheck.needs_llm` is true.
3. Add graph/unit regression tests for budget and quota classify-skip on `AMBIGUOUS_QUESTION`.
4. Confirm obvious analysis with `max_llm_calls=0` still fails later (unchanged deterministic path).
5. Update `docs/TECHNICAL_EXPLANATION.md` input-guard paragraph for classifier-unavailable fail-closed.
6. Bump version to 0.28.0; run pytest + evals; commit.
