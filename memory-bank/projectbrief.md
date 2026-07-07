# Project Brief — Retail Company Data Analysis Chat Assistant

## What we are building

An internal **data analysis chat agent** for a retail company's non-technical executive team (Store and Regional Managers). Executives ask complex natural-language questions about sales, inventory and performance (e.g. *"Why is branch X underperforming and how does it compare to branch Y?"*), and the agent answers with analyst-grade reports backed by live SQL against the company data warehouse.

This repository is the deliverable for the **Opsfleet AI Technical Assignment** (see `docs/AI Technical Assignment - Retail Company.pdf`). It must contain:

1. **Architecture Diagram** (Mermaid) — building blocks, services, data flow.
2. **Detailed technical explanation** — cloud services / LLM / framework choices, data flow, error handling and fallbacks, setup instructions, and how each requirement is handled.
3. **Working prototype** — a CLI chat agent that generates and runs SQL against BigQuery (`bigquery-public-data.thelook_ecommerce`), self-heals on failure, and produces a report.

## Data sources the agent has access to

- **The Database**: read-only SQL access to raw transaction logs — BigQuery public dataset `thelook_ecommerce`, tables: `orders`, `order_items`, `products`, `users`.
- **The "Golden Knowledge" Bucket**: a data lake of historical **Trios** (Question → SQL Query → Analyst Report) created by human experts, used as few-shot/RAG grounding.

## Assignment requirements (all 8, verbatim intent)

| # | Requirement | Summary |
|---|-------------|---------|
| 1 | Hybrid Intelligence | Use the Golden Bucket at query time (retrieval) and explain how it is updated over time. |
| 2 | Safety & PII Masking | Analysis questions only; guard against malicious users; **never** show Customer Phones/Emails, even if SQL retrieves them. |
| 3 | High-Stakes Oversight | Agent manages a "Saved Reports" library; deletes ("Delete all reports mentioning Client X") require a strict confirmation flow without breaking UX; users may delete only their own reports. |
| 4 | Continuous Improvement | User level: remember per-manager format preferences. System level: learn from past interactions. |
| 5 | Resilience & Error Handling | Detect SQL errors / empty results and self-correct before giving up; no UI crashes; no cost inflation; resilient to third-party downtime. |
| 6 | Quality Assurance | How the agent is evaluated pre-deployment; how report correctness vs. user intent is verified. |
| 7 | Observability | Metrics at agent level; deep-dive debugging of message correspondence. |
| 8 | Agility (Persona Management) | Non-developers can change report tone/instructions weekly without redeployment. |

## Prototype scope decision (architect)

The prototype **must** support at least 2 of: PII Masking, High-Stakes Oversight, Resilience, QA, Observability. Decision (2026-07-07, maximum-effort submission): we implement **all five as first-class features** — PII Masking, High-Stakes Oversight, Resilience & Self-heal, Quality Assurance (full eval suite incl. intent-correctness scoring), and Observability. Hybrid Intelligence (golden trios retrieval), personas and user preferences are also implemented, because they are cheap in the chosen architecture and heavily weighted in the design assessment.

## Constraints

- The assignment estimates 6–12 hours; the user has opted for a **maximum-effort submission** beyond that estimate. The assignment's own note still applies: the prototype must stay **simple and working** — effort goes into requirement coverage, tests and polish, not complexity.
- CLI interface only (UIs earn no points).
- Preferably LangGraph / LangChain v1; preferably a newer Gemini model (free AI Studio key, mind rate limits); OpenRouter/Ollama as alternatives.
- Runnable on another machine with plain setup instructions (Docker optional).
- Public GitHub repo: documentation + source + architecture diagram.

## Success criteria

- Assessment focuses on **system design, technical explanation, and an elegant prototype**.
- The agent can answer: customer behavior (top customers, total spend), product performance, time-based metrics (monthly revenue, up-to-date revenue by product), and questions about the database structure.
