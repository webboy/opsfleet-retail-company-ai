---
id: new-customers-by-month
question: How many new customers did we acquire each month?
tags:
  - customers
  - acquisition
  - monthly
sql: |
  SELECT
    FORMAT_TIMESTAMP('%Y-%m', created_at) AS signup_month,
    COUNT(*) AS new_customers
  FROM `bigquery-public-data.thelook_ecommerce.users`
  WHERE created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH))
  GROUP BY signup_month
  ORDER BY signup_month
  LIMIT 24
report: |
  New customer acquisition counts users by signup month using users.created_at over
  the last year.
---
