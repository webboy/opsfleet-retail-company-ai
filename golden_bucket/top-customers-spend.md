---
id: top-customers-spend
question: Who are our top 10 customers by total spend?
tags:
  - customers
  - revenue
  - top-n
sql: |
  SELECT
    u.id AS user_id,
    u.first_name,
    u.last_name,
    SUM(oi.sale_price) AS total_spend
  FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
  JOIN `bigquery-public-data.thelook_ecommerce.orders` o
    ON oi.order_id = o.order_id
  JOIN `bigquery-public-data.thelook_ecommerce.users` u
    ON o.user_id = u.id
  WHERE o.status = 'Complete'
  GROUP BY u.id, u.first_name, u.last_name
  ORDER BY total_spend DESC
  LIMIT 10
report: |
  Rank the top customers by total completed order value. Join order_items to orders
  and users, filter to completed orders, aggregate sale_price, and return the top 10.
---
