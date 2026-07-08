# Task 0014 — PII mask: fully mask name-flagged columns (unformatted phones leak)

## Metadata

- **Task ID**: 0014
- **Title**: PII mask: fully mask name-flagged columns (unformatted phones leak)
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Assignment requirement 2 forbids displaying Customer Phones/Emails **ever**.
In `mask_dataframe`, a column flagged as PII **by name** (e.g. `phone`) still
delegates per-cell masking to shape detection (`_mask_cell_value`), and
`_value_looks_like_phone` deliberately rejects digit-only values without phone
punctuation (to avoid masking numeric amounts/IDs). Result: a `phone` column
containing unformatted numbers like `5551234567` passes through **unmasked**.

## Reproduction (confirmed 2026-07-08)

```python
df = pd.DataFrame({"phone": ["5551234567", "+1 415 555 2671"]})
mask_dataframe(df).dataframe
#   phone
# 0 5551234567     <-- leak
# 1 ***-***-2671
```

`thelook_ecommerce.users` has no phone column, so the live prototype is exposed
mainly via emails (already masked), but the requirement and production design
explicitly cover phones — the deterministic guarantee must hold.

## Scope

- In `src/retail_agent/safety.py::mask_dataframe`, when a column is flagged by
  **name** (`_column_is_pii(column)`), mask every non-null value
  unconditionally (email-shaped → email mask, phone-shaped → phone mask,
  anything else → `***` or last-4-digits style), instead of returning
  unmatched values unchanged.
- Content-flagged columns (detected by value sampling) keep the current
  shape-based per-cell behavior — that path exists to avoid masking numeric
  metrics, which is still correct.
- Remove or fix the misleading `_column_is_pii(text)` call inside
  `_mask_cell_value` (it checks the **value** text against column markers —
  dead/incorrect logic).

### Out of scope

- Output-layer (`mask_text`) heuristics for bare 10-digit numbers in prose —
  indistinguishable from order/user IDs; the DataFrame layer is the correct
  place for the guarantee and the report LLM never sees raw values after it.

## Acceptance criteria

- [ ] Name-flagged PII column with unformatted digit values is fully masked.
- [ ] Name-flagged PII column with arbitrary strings is fully masked (no pass-through).
- [ ] Numeric metric columns (`total_spend`, counts) remain untouched.
- [ ] Existing `tests/test_safety.py` suite green; new regression tests for the cases above.

## References

- `src/retail_agent/safety.py` (`mask_dataframe`, `_mask_cell_value`, `_value_looks_like_phone`)
- `tests/test_safety.py`
- Assignment requirement 2 (Safety & PII Masking), `docs/TECHNICAL_EXPLANATION.md` §2
