---
id: revenue-by-department
question: Which product departments drive the most revenue?
tags:
  - products
  - department
  - revenue
sql: |
  SELECT
    p.department,
    SUM(oi.sale_price) AS revenue
  FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
  JOIN `bigquery-public-data.thelook_ecommerce.products` p
    ON oi.product_id = p.id
  JOIN `bigquery-public-data.thelook_ecommerce.orders` o
    ON oi.order_id = o.order_id
  WHERE o.status = 'Complete'
  GROUP BY p.department
  ORDER BY revenue DESC
  LIMIT 15
report: |
  Roll up revenue by product department for completed orders to see which parts of
  the catalog drive sales.
---
