# Task 0026 — Submission docs alignment

## Metadata

- **Task ID**: 0026
- **Title**: Submission docs alignment
- **Status**: todo
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Align human-facing documentation with the original assignment and the actual shipped prototype. Reviewers should not see branch/inventory examples, CI/token-metric overclaims, or unclear setup/eval instructions that the code does not support.

## Scope

- Replace unsupported branch/inventory examples with dataset-faithful examples from `thelook_ecommerce`.
- Add or improve a "supported questions" matrix for customer behavior, product performance, time metrics, and schema questions.
- Document schema-question support and the static schema asset at a reviewer-facing level.
- Fix setup risks: clone placeholder if possible, BigQuery billing-project note, live eval `--no-compare` guidance.
- Correct overclaims: token metrics if not implemented, "CI blocks deploy" if CI is not present yet, "optional" candidate capture wording, eval case count/threshold.
- Ensure human docs do not reference internal memory-bank/task workflow.

### Out of scope

- Implementing new runtime behavior unless a doc statement must be backed by code.
- Writing a new long architecture document from scratch.
- Changing assignment PDF contents.

## Acceptance criteria

- [ ] README and docs avoid unsupported branch/inventory claims for the shipped dataset.
- [ ] Human docs include a concise supported-question matrix mapped to assignment expected capabilities.
- [ ] Schema-question behavior is documented in the human docs.
- [ ] Eval, CI, token, candidate-capture, and live baseline wording matches the actual implementation.
- [ ] Setup instructions mention BigQuery billing-project expectations clearly.
- [ ] `rg "memory-bank|task 0|\\.cursor" README.md docs/` returns no forbidden internal workflow references, except intentional MCP client configuration if retained and justified.
- [ ] Documentation-only verification is recorded in `HANDOFF.md`.

## References

- Review finding: branch/inventory examples overpromise capabilities not in the public dataset.
- Review finding: schema route exists in code but is under-documented for reviewers.
- Review finding: docs promise token metrics/CI behavior not fully implemented.
- Docs: `README.md`, `docs/ARCHITECTURE.md`, `docs/TECHNICAL_EXPLANATION.md`, `docs/USAGE.md`, `docs/EVALUATION.md`, `docs/MCP.md`.
- Assignment deliverables: architecture diagram, technical explanation, setup/example run, requirement handling.
