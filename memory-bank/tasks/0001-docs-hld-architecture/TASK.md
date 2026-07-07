# Task 0001 — HLD, architecture diagram & technical explanation

## Metadata

- **Task ID**: 0001
- **Title**: HLD, architecture diagram & technical explanation
- **Status**: todo
- **Owner**: Engineer
- **Created**: 2026-07-07
- **Updated**: 2026-07-07

## Goal

Produce the assignment's primary deliverable: a production-grade High-Level Design with a Mermaid architecture diagram and a detailed technical explanation that covers all 8 requirements, the chosen services/models/frameworks, data flows, and error/fallback strategies.

## Scope

- `docs/ARCHITECTURE.md`: production HLD — Mermaid diagram(s) of building blocks, services and flows; component responsibilities; where data is stored and handled; how the system extends (graphs, e-mail reports, new data sources).
- `docs/TECHNICAL_EXPLANATION.md` (or merged into ARCHITECTURE.md if it reads better): reasoning for cloud services / LLM / framework choices; data flow between components; error handling and fallback strategies; an explicit **requirement-by-requirement** section explaining how each of the 8 requirements is solved (including Golden Bucket update strategy and query-time retrieval, QA/eval strategy, observability metrics, persona management).
- Keep the production design consistent with the prototype decisions in `memory-bank/systemPatterns.md`; where production differs from prototype (e.g. Vertex AI Vector Search vs. local files), state both explicitly.
- These are **human-facing documents** — per `documentation-separation.mdc` they must be self-contained and must not reference `memory-bank/`, task IDs or the agent workflow.

### Out of scope

- Application code, README setup instructions (task 0009).

## Acceptance criteria

- [ ] Mermaid diagram(s) render on GitHub and show all building blocks, services and data flow.
- [ ] Every one of the 8 requirements has a dedicated, concrete explanation (not hand-waving) of how it is handled in production.
- [ ] Cloud service, LLM and framework choices are each justified with reasoning.
- [ ] Error handling / fallback strategies are described (LLM downtime, BigQuery failure, bad SQL, rate limits).
- [ ] Golden Bucket lifecycle is explained: query-time retrieval AND how the bucket is updated/curated over time.
- [ ] Document is detailed enough for a reviewer to understand how the system functions in production.
- [ ] No references to `memory-bank/`, tasks or agent workflow anywhere in `docs/` (self-contained human documentation).

## References

- `docs/AI Technical Assignment - Retail Company.pdf` (Deliverables 1–2)
- `memory-bank/projectbrief.md`, `memory-bank/systemPatterns.md`, `memory-bank/techContext.md`
