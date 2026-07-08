# Handoff — Task 0034

## Summary

Keyword-based Golden Bucket fallback now requires at least `GOLDEN_KEYWORD_MIN_OVERLAP` shared tokens (default **2**) between the user question and a stored trio. Weak single-token overlaps no longer inject misleading few-shot examples; zero overlap and genuinely relevant multi-token matches behave as before.

## Changed files

- `src/retail_agent/config.py` — `keyword_min_overlap` setting + `GOLDEN_KEYWORD_MIN_OVERLAP` env (default 2)
- `src/retail_agent/golden.py` — `_keyword_overlap`, `_retrieve_by_keywords` floor enforcement
- `tests/test_golden.py` — regression for weak single-token overlap
- `tests/helpers.py` — default setting in `make_settings`
- Eval/judge Settings constructors — new field
- `.env.example`, `docs/ARCHITECTURE.md`, `docs/TECHNICAL_EXPLANATION.md`
- Version **0.29.0** in `pyproject.toml` and `src/retail_agent/__init__.py`

## Verification

```bash
pytest tests/test_golden.py tests/test_golden_graph.py tests/test_mcp_server.py -q   # 27 passed
pytest -q                                                                            # 236 passed
python -m retail_agent.evals                                                         # 17/17 passed
```

## Acceptance criteria

- [x] No-overlap keyword fallback still returns empty.
- [x] Weak one-token overlap filtered (`monthly sales trends` → empty).
- [x] Genuinely relevant keyword fallback still retrieves trios (`monthly revenue last year`).
- [x] Full pytest and dry-run eval pass.
- [x] Docs and task metadata updated; version bumped.

## Risks / rollback

- Low risk. Very short questions that share only one meaningful token with a trio will no longer retrieve via keyword fallback; increase `GOLDEN_KEYWORD_MIN_OVERLAP=1` if needed for a specific deployment.
- Revert commit to restore score > 0-only filtering.
