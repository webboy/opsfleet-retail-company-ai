---
id: monthly-revenue
question: What was our monthly revenue last year?
tags:
  - revenue
  - time-series
  - monthly
sql: |
  SELECT
    FORMAT_TIMESTAMP('%Y-%m', o.created_at) AS month,
    SUM(oi.sale_price) AS revenue
  FROM `bigquery-public-data.thelook_ecommerce.orders` o
  JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi
    ON o.order_id = oi.order_id
  WHERE o.status = 'Complete'
    AND o.created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH))
  GROUP BY month
  ORDER BY month
  LIMIT 24
report: |
  Monthly revenue is the sum of completed order line sale_price grouped by order month.
  Use orders.created_at for the time bucket and filter to roughly the last 12 months.
---
