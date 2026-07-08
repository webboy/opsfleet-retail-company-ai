# Task Index

Quick overview of all tasks. Source of truth for each row is the task's `TASK.md` → Metadata. See `.cursor/rules/task-index-workflow.mdc`.

| ID | Title | Status | Owner | Updated |
|------|-------|--------|-------|---------|
| 0001 | HLD, architecture diagram & technical explanation | done | Engineer | 2026-07-07 |
| 0002 | Project scaffolding, config & BigQuery foundation | done | Engineer | 2026-07-07 |
| 0003 | Agent core: LangGraph, SQL generation, self-heal, CLI | done | Engineer | 2026-07-07 |
| 0004 | Hybrid Intelligence: Golden Bucket trio retrieval | done | Engineer | 2026-07-07 |
| 0005 | Safety: input guard & PII masking | done | Engineer | 2026-07-07 |
| 0006 | High-Stakes Oversight: saved reports & delete confirmation | done | Engineer | 2026-07-07 |
| 0007 | Learning loop: user preferences & personas | done | Engineer | 2026-07-07 |
| 0008 | Observability & QA evaluation suite | done | Engineer | 2026-07-08 |
| 0009 | Final accompanying documentation & submission polish | done | Engineer | 2026-07-08 |
| 0010 | Optional: expose guarded capabilities as an MCP server | done | Engineer | 2026-07-08 |
| 0011 | LLM provider fallback: OpenRouter / Ollama | done | Engineer | 2026-07-07 |
| 0012 | Fix sql_guard: allow CTE (WITH) queries | done | Engineer | 2026-07-08 |
| 0013 | Fix LLM call budget: reset per turn, not per thread | done | Engineer | 2026-07-08 |
| 0014 | PII mask: fully mask name-flagged columns (unformatted phones leak) | done | Engineer | 2026-07-08 |
| 0015 | LLM resilience: retry/fallback on connection-level outages | done | Engineer | 2026-07-08 |
| 0016 | Polish: stale CLI diagnostics, docs test-count drift, brittle live eval assertion | done | Engineer | 2026-07-08 |
| 0017 | PII column markers over-match: legit metrics masked to `***` (regression of 0014) | done | Engineer | 2026-07-08 |
| 0018 | /save persists non-analysis output as a "report" | done | Engineer | 2026-07-08 |
| 0019 | Golden Bucket robustness: one malformed trio file crashes the CLI | done | Engineer | 2026-07-08 |
| 0020 | Preference regex hijacks analysis questions mentioning "table" | done | Engineer | 2026-07-08 |
| 0021 | Polish: eval --layer phantom regressions, inflated self-heal metric, stale trace fields, .env precedence | done | Engineer | 2026-07-08 |
| 0022 | SQL cost controls and MCP payload caps | done | Engineer | 2026-07-08 |
| 0023 | Input guard structured labels | done | Engineer | 2026-07-08 |
| 0024 | Empty results and live eval regression | done | Engineer | 2026-07-08 |
| 0025 | CI and eval gate hardening | todo | Engineer | 2026-07-08 |
| 0026 | Submission docs alignment | todo | Engineer | 2026-07-08 |
| 0027 | Golden Bucket and learning-loop hardening | todo | Engineer | 2026-07-08 |
