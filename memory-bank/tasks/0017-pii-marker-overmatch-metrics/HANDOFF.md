# Handoff — Task 0017

## Summary

Fixed PII column marker over-matching that caused legitimate metric columns (`cancelled_rate`, `email_count`, etc.) to be unconditionally masked to `***` after task 0014. Replaced substring matching with token-boundary matching and exempted numeric dtypes from name-based masking while preserving strict masking for string PII columns.

## Changed files

- `src/retail_agent/safety.py` — `_column_name_tokens()`, token-boundary `_column_is_pii()`, numeric dtype exemption in `mask_dataframe()`
- `tests/test_safety.py` — false-positive and true-positive parametric tests
- `tests/test_safety_graph.py` — cancelled-rate graph regression test
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.15.0**
- `memory-bank/tasks/0017-pii-marker-overmatch-metrics/*` — task docs
- `memory-bank/activeContext.md`, `memory-bank/progress.md`

## Impact

- Metric columns whose names contain PII marker substrings (e.g. `cancelled_rate` containing `cell`, `email_count` containing `email`) are no longer masked when numeric.
- String columns with PII marker tokens (`email`, `phone_number`, `mobile`, `contact_info`) remain fully masked per task 0014.
- Content-based PII detection unchanged.

## How to verify

```bash
pytest tests/test_safety.py tests/test_safety_graph.py -q
pytest -q
python -m retail_agent.evals
```

Optional live sanity (requires configured LLM + BigQuery):

```bash
retail-agent chat
# Ask: What share of orders are cancelled?
# Expect a numeric cancellation share, not *** values or a spurious PII policy note.
```

## Risks / rollback

- **Low risk**: numeric columns cannot contain email/phone strings; token matching is stricter than substring matching.
- **Rollback**: revert commit; task 0014 string PII masking behavior is preserved by existing tests.

## Acceptance criteria check

- [x] `mask_dataframe` leaves `cancelled_rate`, `excellent_score`, `miscellaneous`, `email_count` (numeric), `phone_orders` (numeric) untouched.
- [x] `email`, `customer_email`, `phone_number`, `mobile`, `contact_info` string columns are still fully masked (0014 tests green).
- [x] Graph-level test: cancelled-rate style result reaches compose-report prompt unmasked with no PII policy note.
- [ ] Live sanity — not run in this session; user can confirm with live CLI.
