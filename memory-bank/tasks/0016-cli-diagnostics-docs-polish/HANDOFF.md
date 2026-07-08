# Handoff — Task 0016

## Summary

Polish bundle: CLI now prints `[sql attempts]` / `[retrieved trios]` only on completed analysis turns; eval live assertions no longer require data-dependent tokens (`denim`, `search`); `docs/EVALUATION.md` no longer hard-codes a stale pytest count.

## Changed files

- `src/retail_agent/cli.py` — `_should_print_analysis_diagnostics()` gates diagnostic output on `guard_route == "analysis"`
- `tests/test_cli.py` — unit + graph regression tests for analysis vs save/list/prefs turns
- `evals/cases.yaml` — relaxed `top-products-sales` and `revenue-by-traffic-source` report assertions
- `docs/EVALUATION.md` — pytest count wording avoids drift
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.14.0**
- `memory-bank/` — task docs, `activeContext.md`, `progress.md`

## Impact

- **UX**: save/list/prefs/delete turns no longer show stale SQL/trio lines from the prior analysis turn.
- **Evals**: live capability checks remain property-based; dry-run fixtures unchanged in intent.
- **Docs**: reviewers run `pytest -q` for current count instead of trusting a frozen number.

## How to verify

1. `pytest tests/test_cli.py -q` — 8 passed
2. `pytest tests/test_eval_runner.py tests/test_eval_assertions.py -q` — 5 passed
3. `pytest -q` — **157 passed**
4. `python -m retail_agent.evals` — **16/16** dry-run
5. Live CLI: ask an analysis question (see diagnostics), then `/save` or `show my reports` (no stale diagnostics)

## Risks / rollback

- Graph state still retains prior SQL/trios for save/report flows; only CLI display changed.
- Rollback: revert commits and restore `0.13.0`.

## Acceptance criteria check

- [x] No stale diagnostics after save/list/prefs turns; still shown after analysis
- [x] `docs/EVALUATION.md` no longer states stale test count
- [x] Dry-run eval 16/16, no baseline regressions
- [x] Live eval assertions no longer require `denim` / `search` tokens
