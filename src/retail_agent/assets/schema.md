# BigQuery schema — `bigquery-public-data.thelook_ecommerce`

Read-only dataset. Only these four tables are allowed in generated SQL.

## orders

Customer order headers.

| Column | Type | Notes |
|--------|------|-------|
| order_id | INT64 | Primary key |
| user_id | INT64 | FK → users.user_id |
| status | STRING | e.g. Complete, Cancelled, Processing |
| gender | STRING | |
| created_at | TIMESTAMP | Order creation time |
| returned_at | TIMESTAMP | Nullable |
| shipped_at | TIMESTAMP | Nullable |
| delivered_at | TIMESTAMP | Nullable |
| num_of_item | INT64 | Item count on order |

## order_items

Line items per order.

| Column | Type | Notes |
|--------|------|-------|
| order_item_id | INT64 | Primary key |
| order_id | INT64 | FK → orders.order_id |
| product_id | INT64 | FK → products.id |
| inventory_item_id | INT64 | |
| sale_price | FLOAT64 | Price paid for line item |
| created_at | TIMESTAMP | |
| shipped_at | TIMESTAMP | Nullable |
| delivered_at | TIMESTAMP | Nullable |
| returned_at | TIMESTAMP | Nullable |

## products

Product catalog.

| Column | Type | Notes |
|--------|------|-------|
| id | INT64 | Primary key (product id) |
| cost | FLOAT64 | |
| category | STRING | e.g. Intimates, Jeans |
| name | STRING | Product name |
| brand | STRING | |
| retail_price | FLOAT64 | List price |
| department | STRING | |
| sku | STRING | |
| distribution_center_id | INT64 | |

## users

Customer demographics (contains PII — emails in raw data; masking handled in later pipeline stages).

| Column | Type | Notes |
|--------|------|-------|
| id | INT64 | Primary key (user id) |
| first_name | STRING | |
| last_name | STRING | |
| email | STRING | PII |
| age | INT64 | |
| gender | STRING | |
| state | STRING | |
| street_address | STRING | |
| postal_code | STRING | |
| city | STRING | |
| country | STRING | |
| latitude | FLOAT64 | |
| longitude | FLOAT64 | |
| traffic_source | STRING | |
| created_at | TIMESTAMP | |

## Common joins

- `orders.user_id = users.id`
- `order_items.order_id = orders.order_id`
- `order_items.product_id = products.id`

## Query notes

- Use fully qualified table names: `` `bigquery-public-data.thelook_ecommerce.orders` ``
- Revenue metrics typically sum `order_items.sale_price` for completed orders.
- Time filters usually use `orders.created_at` or `order_items.created_at`.
- Always include a reasonable `LIMIT` (the sql_guard will inject one if missing).
