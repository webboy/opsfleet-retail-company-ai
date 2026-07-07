---
id: top-products-sales
question: Which products sold the most units?
tags:
  - products
  - performance
  - top-n
sql: |
  SELECT
    p.id AS product_id,
    p.name,
    p.category,
    COUNT(*) AS units_sold,
    SUM(oi.sale_price) AS revenue
  FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
  JOIN `bigquery-public-data.thelook_ecommerce.products` p
    ON oi.product_id = p.id
  JOIN `bigquery-public-data.thelook_ecommerce.orders` o
    ON oi.order_id = o.order_id
  WHERE o.status = 'Complete'
  GROUP BY p.id, p.name, p.category
  ORDER BY units_sold DESC
  LIMIT 15
report: |
  Product performance by units sold counts order_items rows for completed orders,
  grouped by product with revenue as a secondary metric.
---
