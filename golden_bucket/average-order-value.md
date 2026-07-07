---
id: average-order-value
question: What is our average order value?
tags:
  - orders
  - revenue
  - kpi
sql: |
  SELECT
    AVG(order_total) AS average_order_value,
    COUNT(*) AS order_count
  FROM (
    SELECT
      o.order_id,
      SUM(oi.sale_price) AS order_total
    FROM `bigquery-public-data.thelook_ecommerce.orders` o
    JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi
      ON o.order_id = oi.order_id
    WHERE o.status = 'Complete'
    GROUP BY o.order_id
  )
  LIMIT 1
report: |
  Average order value is the mean of per-order totals (sum of line sale_price) for
  completed orders only.
---
