# Task 0017 — PII column markers over-match: legit metrics masked to `***` (regression of 0014)

## Metadata

- **Task ID**: 0017
- **Title**: PII column markers over-match: legit metrics masked to `***` (regression of 0014)
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

`_column_is_pii` does substring matching against `PII_COLUMN_MARKERS`. The
marker `"cell"` matches inside **cancelled**, ex**cell**ent, mis**cell**aneous;
`"email"`/`"phone"`/`"contact"` match metric columns like `email_count`,
`phone_orders`, `users_contacted`. Before task 0014 this was mostly harmless
(numeric values didn't look like emails/phones so they passed through). After
0014's — correct in intent — **unconditional** masking of name-flagged
columns, these false positives now destroy legitimate analytics.

## Reproduction (confirmed 2026-07-08, end-to-end through the graph)

Question "what share of orders are cancelled?" with result columns
`cancelled_rate, email_count` — the report LLM receives:

```
cancelled_rate,email_count
***,***
```

with `pii_masked_columns=['cancelled_rate', 'email_count']` and a spurious
"contact details masked" policy note. The agent can no longer answer
cancellation-rate questions with real numbers (a documented seed-trio /
eval-case capability — `evals/cases.yaml` `cancelled-order-rate`,
`golden_bucket/cancelled-order-rate.md`). Dry-run evals do NOT catch this
because `ScriptLLM` ignores its input.

## Scope

- Replace substring marker matching with **token-boundary** matching on the
  column name (split on `_`, digits, case boundaries): flag `email`,
  `e_mail`, `phone`, `mobile`, `cell`, `telephone`, `contact`, `fax` only as
  whole tokens. `cancelled_rate` must not match; `customer_email` and
  `phone_number` must.
- Exempt **numeric-dtype** columns from name-based unconditional masking: a
  numeric column cannot contain an email/phone string, so `email_count`
  (INT64) stays intact even though the token `email` appears. Keep string
  columns strictly masked per 0014.
- Add a dry-run-visible guard: an eval or unit test asserting
  `result_preview` for the cancelled-rate case contains the numeric value
  (i.e. this class of regression fails tests, not just live runs).

### Out of scope

- Content-based detection changes (value sampling logic stays as is).

## Acceptance criteria

- [x] `mask_dataframe` leaves `cancelled_rate`, `excellent_score`, `miscellaneous`, `email_count` (numeric), `phone_orders` (numeric) untouched.
- [x] `email`, `customer_email`, `phone_number`, `mobile`, `contact_info` string columns are still fully masked (0014 guarantees hold; its tests stay green).
- [x] Graph-level test: cancelled-rate style result reaches `result_preview` unmasked with no PII policy note.
- [x] Live sanity: "What share of orders are cancelled?" produces a numeric answer (subject to live model SQL quality).

## References

- `src/retail_agent/safety.py` (`PII_COLUMN_MARKERS`, `_column_is_pii`, `mask_dataframe`, `_mask_pii_named_cell_value`)
- Task 0014 (introduced unconditional masking; correct but amplified marker over-match)
- `evals/cases.yaml` (`cancelled-order-rate`), `golden_bucket/cancelled-order-rate.md`
- Assignment requirement 2 (PII) vs. expected capability (product/order metrics)
