---
id: product-category-revenue
question: What are the top product categories by revenue?
tags:
  - products
  - category
  - revenue
sql: |
  SELECT
    p.category,
    SUM(oi.sale_price) AS revenue,
    COUNT(DISTINCT oi.order_id) AS order_count
  FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
  JOIN `bigquery-public-data.thelook_ecommerce.products` p
    ON oi.product_id = p.id
  JOIN `bigquery-public-data.thelook_ecommerce.orders` o
    ON oi.order_id = o.order_id
  WHERE o.status = 'Complete'
  GROUP BY p.category
  ORDER BY revenue DESC
  LIMIT 20
report: |
  Compare product categories by total revenue from completed orders. Join order_items
  to products for category and to orders to exclude non-complete orders.
---
