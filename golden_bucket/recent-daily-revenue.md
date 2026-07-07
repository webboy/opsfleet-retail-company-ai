---
id: recent-daily-revenue
question: What was daily revenue over the last 30 days?
tags:
  - revenue
  - daily
  - time-series
sql: |
  SELECT
    DATE(o.created_at) AS order_date,
    SUM(oi.sale_price) AS revenue
  FROM `bigquery-public-data.thelook_ecommerce.orders` o
  JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi
    ON o.order_id = oi.order_id
  WHERE o.status = 'Complete'
    AND o.created_at >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY))
  GROUP BY order_date
  ORDER BY order_date
  LIMIT 31
report: |
  Daily revenue trend for the last 30 days using completed orders. Good follow-up
  anchor when the user asks about recent performance or "last month".
---
