# Handoff — Task 0026

## Summary

User approved. Human-facing docs aligned with the shipped prototype and `thelook_ecommerce` dataset via `docs/SCHEMA.md` and README/docs drift fixes. Documentation-only — no version bump.

## Changed files

- `docs/SCHEMA.md` — new reviewer-facing schema/supported-questions page
- `README.md` — doc map link, billing project note, unsupported-dimension example
- `docs/ARCHITECTURE.md` — dataset-faithful examples, turn-flow Mermaid (schema/chitchat/empty results), candidate capture wording
- `docs/TECHNICAL_EXPLANATION.md` — schema route, 11+5 eval structure, judge threshold, metrics without tokens, self-heal vs empty results, `--live --no-compare`
- `docs/USAGE.md` — schema link, billing/ADC notes, automatic candidate capture
- `docs/EVALUATION.md` — judge threshold, historical baseline filename note, schema case link
- `docs/MCP.md` — concrete local verification commands
- `memory-bank/tasks/0026-submission-docs-alignment/*`, `INDEX.md`, `activeContext.md`, `progress.md`

## Impact

- Documentation-only delivery — **no version bump** (project remains **0.22.0**).
- No runtime or eval behavior changes.

## How to verify

1. Documentation separation:
   ```bash
   rg "memory-bank|task 0" README.md docs/    # expect no matches
   rg "\.cursor" README.md docs/              # only docs/MCP.md (intentional MCP client setup)
   ```
2. Dry-run eval (setup/eval docs touched):
   ```bash
   python -m retail_agent.evals               # expect 16/16 passed
   ```
3. Manual spot-check: open `docs/SCHEMA.md` and confirm supported-question matrix matches `evals/cases.yaml`.

## Risks / rollback

- Low risk — docs only. Revert the commit to restore prior wording.

## Acceptance criteria check

- [x] README and docs avoid unsupported branch/inventory claims for the shipped dataset — replaced or labeled as unsupported boundaries
- [x] Human docs include supported-question matrix mapped to assignment capabilities — `docs/SCHEMA.md`
- [x] Schema-question behavior documented — `docs/SCHEMA.md#schema-question-route` + cross-links
- [x] Eval, CI, token, candidate-capture, and live baseline wording matches implementation
- [x] Setup instructions mention BigQuery billing-project expectations — README, USAGE, SCHEMA
- [x] `rg "memory-bank|task 0" README.md docs/` returns nothing; `.cursor` only in MCP.md
- [x] Documentation-only verification recorded in this HANDOFF
