---
id: revenue-by-traffic-source
question: How does revenue compare across customer traffic sources?
tags:
  - customers
  - marketing
  - revenue
sql: |
  SELECT
    u.traffic_source,
    SUM(oi.sale_price) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders
  FROM `bigquery-public-data.thelook_ecommerce.orders` o
  JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi
    ON o.order_id = oi.order_id
  JOIN `bigquery-public-data.thelook_ecommerce.users` u
    ON o.user_id = u.id
  WHERE o.status = 'Complete'
  GROUP BY u.traffic_source
  ORDER BY revenue DESC
  LIMIT 20
report: |
  Attribute revenue to the customer's traffic_source from the users table. Useful for
  comparing acquisition channels by completed order value.
---
