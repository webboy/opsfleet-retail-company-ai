# Plan — Task 0017

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Rewrite `_column_is_pii` to tokenize the column name (`re.split(r"[^a-z]+", name.lower())` plus camelCase splitting) and require whole-token marker matches.
2. In `mask_dataframe`, skip name-based unconditional masking for numeric-dtype columns (`pd.api.types.is_numeric_dtype`); string columns keep 0014 behavior.
3. Tests: false-positive matrix (`cancelled_rate`, `excellent_score`, `miscellaneous`, `email_count` numeric, `phone_orders` numeric) + true-positive matrix (`email`, `customer_email`, `phone_number`, `contact_info` strings); graph-level `result_preview` assertion for the cancelled-rate shape.
4. Docs: none (behavior now matches documented intent); WORKLOG notes the 0014 interaction.
5. Commit: `fix(safety): token-match PII column markers, exempt numeric metrics (task 0017)` + minor version bump.
