---
id: cancelled-order-rate
question: What share of orders are cancelled?
tags:
  - orders
  - cancellations
  - operations
sql: |
  SELECT
    status,
    COUNT(*) AS order_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_orders
  FROM `bigquery-public-data.thelook_ecommerce.orders`
  GROUP BY status
  ORDER BY order_count DESC
  LIMIT 10
report: |
  Order status mix shows operational health. Group orders by status and compute each
  status as a percentage of all orders.
---
