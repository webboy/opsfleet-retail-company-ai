# Worklog — Task 0026

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-08

- Created from the strict assignment review. Primary risks: human docs overuse assignment branch/inventory language, under-document schema support, and include some implementation-drift wording.

## 2026-07-08 (implementation)

- Added `docs/SCHEMA.md`: supported-question matrix (11 capability cases), tables/joins, dataset boundaries, schema route, billing project note.
- Updated `README.md`: SCHEMA link in doc map, GCP billing project clarification, unsupported-dimension example label.
- Updated `docs/ARCHITECTURE.md`: dataset-faithful problem statement, turn-flow Mermaid (schema/chitchat/prefs, empty results → report), automatic candidate capture wording.
- Updated `docs/TECHNICAL_EXPLANATION.md`: removed token metrics overclaim, fixed empty-result self-heal drift, 11+5 eval cases, judge threshold, `--live --no-compare`, schema route link.
- Updated `docs/USAGE.md`, `docs/EVALUATION.md`, `docs/MCP.md` per plan.
- Verification: `rg "memory-bank|task 0" README.md docs/` clean; `.cursor` only in MCP.md; dry-run eval 16/16 passed.
- No version bump (documentation-only).
