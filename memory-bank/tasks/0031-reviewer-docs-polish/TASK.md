# Task 0031 — Reviewer docs polish

## Metadata

- **Task ID**: 0031
- **Title**: Reviewer docs polish
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Remove the last reviewer-facing documentation friction from setup and example evidence.

## Scope

- Replace or clarify the README clone URL placeholder.
- Make README example-session diagnostics match actual CLI output.
- Add explicit examples for destructive delete variants required by the assignment, especially "delete reports made today".
- Label production-only data-flow sections clearly where needed.
- Add any missing license/setup clarification if quick and appropriate.

### Out of scope

- Changing runtime behavior unless docs reveal a real bug.
- Writing a full new documentation package.

## Acceptance criteria

- [x] README setup is copy-paste friendly or clearly explains where to substitute the repository URL.
- [x] Example transcript does not show non-existent CLI diagnostics as if they are real output.
- [x] Human docs demonstrate mention-delete and today-delete confirmation flows.
- [x] Production-only architecture wording is clearly labeled.
- [x] Documentation separation checks pass.
- [x] If commands changed, `python -m retail_agent.evals` still passes.
- [x] Task metadata, `INDEX.md`, `WORKLOG.md`, and `HANDOFF.md` are updated when complete.

## References

- Final review findings: clone placeholder, illustrative CLI transcript drift, missing delete-by-today example, production/prototype wording drift.
- Docs: `README.md`, `docs/ARCHITECTURE.md`, `docs/USAGE.md`, `docs/TECHNICAL_EXPLANATION.md`.
