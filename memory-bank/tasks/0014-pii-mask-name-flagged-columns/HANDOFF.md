# Handoff — Task 0014

## Summary

Fixed `mask_dataframe` so columns flagged by PII name markers (`phone`, `email`, `contact`, etc.) use a strict cell masker that never returns the original non-null value. Content-detected columns keep the existing shape-based `_mask_cell_value` path.

## Changed files

- `src/retail_agent/safety.py` — split name-flagged vs content-detected masking; added `_mask_pii_named_cell_value`; removed dead `_column_is_pii(text)` branch from `_mask_cell_value`
- `tests/test_safety.py` — regression tests for unformatted phones, arbitrary strings in name-flagged columns, content-flagged shape-based masking, numeric columns untouched
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.12.0**
- `memory-bank/` — task docs, `activeContext.md`, `progress.md`

## Impact

- **Behavior change**: `phone`/`mobile`/`email`/etc. columns now mask all non-null values (emails → email mask, ≥7 digits → phone mask, else `***`).
- **No change** to content-detected columns (still shape-based) or numeric metric columns.
- **Out of scope**: `mask_text` output-layer behavior for bare digits in prose.

## How to verify

1. `pytest tests/test_safety.py tests/test_safety_graph.py -q` — 21 passed
2. `pytest -q` — 139 passed
3. `python -m retail_agent.evals` — 16/16 dry-run
4. Quick sanity:
   ```python
   import pandas as pd
   from retail_agent.safety import mask_dataframe
   mask_dataframe(pd.DataFrame({"phone": ["5551234567"]})).dataframe.loc[0, "phone"]
   # → '***-***-4567'
   ```

## Risks / rollback

- Stricter masking applies only to name-flagged columns; revenue/ID columns without PII markers are unaffected.
- Rollback: revert commit and restore `0.11.0`.

## Acceptance criteria check

- [x] `phone` column with `5551234567` masks to `***-***-4567`
- [x] Name-flagged PII column with arbitrary strings masks to `***`
- [x] Content-flagged mixed column masks only email/formatted phone values
- [x] Numeric metric columns remain untouched
- [x] Tests pass; eval dry-run 16/16; version bumped to 0.12.0
