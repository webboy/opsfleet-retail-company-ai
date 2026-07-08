# Schema and Supported Questions

This page describes what the **shipped prototype** can answer against the public BigQuery dataset `bigquery-public-data.thelook_ecommerce`. It is the reviewer-facing summary of the static schema asset used by the agent (`src/retail_agent/assets/schema.md`).

See also: [Usage Guide](./USAGE.md), [Evaluation Guide](./EVALUATION.md), [Architecture](./ARCHITECTURE.md).

## Dataset boundaries

The prototype queries **four read-only tables** only. There is **no** branch, store, warehouse, or inventory stock-level data in this public dataset.

| Supported in prototype | Not in this dataset |
|------------------------|---------------------|
| Revenue and order metrics (`orders`, `order_items`) | Branch / store comparisons |
| Product `category`, `department`, `brand`, `name` | Inventory on-hand or stock levels |
| Customer `state`, `country`, `traffic_source`, demographics | Geographic `region` as a dedicated column |
| Order and line-item statuses, timestamps | Company-specific internal tables |

If a question asks for an unsupported dimension (for example *"revenue by region"*), the agent may retry SQL generation and then explain that the column is not available, suggesting supported alternatives such as `department`, `traffic_source`, or `category`.

## Allowed tables

| Table | Role |
|-------|------|
| `orders` | Order headers — status, timestamps, item count |
| `order_items` | Line items — `sale_price`, product link, line status |
| `products` | Catalog — `category`, `department`, `brand`, prices |
| `users` | Customer demographics — location, `traffic_source`, age (PII masked in output) |

Use fully qualified names, for example:

```sql
`bigquery-public-data.thelook_ecommerce.orders`
```

## Common joins

- `orders.user_id = users.id`
- `order_items.order_id = orders.order_id`
- `order_items.user_id = users.id`
- `order_items.product_id = products.id`

Revenue metrics typically sum `order_items.sale_price` for completed orders (`orders.status = 'Complete'`). Time filters usually use `orders.created_at` or `order_items.created_at`.

## Supported-question matrix

The eval suite (`evals/cases.yaml`) maps prototype capabilities to the assignment's expected question types. Exact numeric answers are **not** asserted — the public dataset is rolling — but SQL shape and report intent are checked.

| Assignment category | Example questions | Primary tables | Eval case ID |
|--------------------|-------------------|----------------|--------------|
| **Customer behavior** | Who are our top customers by spend? What share of orders are cancelled? How does revenue compare across traffic sources? | `users`, `orders`, `order_items` | `top-customers-spend`, `cancelled-order-rate`, `revenue-by-traffic-source` |
| **Product performance** | Which products sold the most? Top categories or departments by revenue? | `products`, `order_items` | `top-products-sales`, `product-category-revenue`, `revenue-by-department` |
| **Time metrics** | Monthly revenue last year? Daily revenue over the last 30 days? New customers by month? Average order value? | `orders`, `order_items`, `users` | `monthly-revenue`, `recent-daily-revenue`, `new-customers-by-month`, `average-order-value` |
| **Schema questions** | What tables and columns do you have? | *(none — static docs only)* | `schema-tables` |

**Safety cases** (injection, off-topic, PII masking, guarded delete, destructive SQL) are documented in the [Evaluation Guide](./EVALUATION.md).

## Schema-question route

Questions about database structure (for example *"What tables do you have?"*) are classified as **schema** turns:

1. `input_guard` routes to `answer_schema` — no Golden Bucket retrieval, no BigQuery job.
2. The LLM answers from the bundled schema documentation only.
3. The eval case `schema-tables` asserts `max_bq_calls: 0`.

This keeps schema answers accurate and avoids query cost for metadata questions.

## BigQuery billing project

Live queries require:

- **`GCP_PROJECT_ID`** — your Google Cloud project used for BigQuery **billing** (job submission), even when reading the public dataset.
- **`gcloud auth application-default login`** — Application Default Credentials for the BigQuery client.

The dataset itself lives in `bigquery-public-data`; your project is not charged for storage, but query jobs are attributed to your billing project.

## Related documentation

- [Usage Guide — environment variables](./USAGE.md#environment-variables)
- [Evaluation Guide — capability cases](./EVALUATION.md#three-layers)
- [Technical Explanation — BigQuery guardrails](./TECHNICAL_EXPLANATION.md#data-warehouse-google-bigquery)
