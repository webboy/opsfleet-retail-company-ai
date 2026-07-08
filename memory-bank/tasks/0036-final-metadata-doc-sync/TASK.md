# Task 0036 — Final metadata and doc sync

## Metadata

- **Task ID**: 0036
- **Title**: Final metadata and doc sync
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

Resolve the last review polish items before submission: remove stale save-flow wording and synchronize task metadata for final handoff.

## Scope

- Remove stale "optional prompt to save" wording from human-facing docs.
- Remove project-internal `.cursor` references from human-facing MCP docs.
- Align `TASK.md`, `INDEX.md`, `activeContext.md`, and `progress.md` for tasks that were already approved as done.
- Record verification and commit the documentation/memory-bank changes.

### Out of scope

- Runtime behavior changes.
- Version bump.
- Live eval rerun.

## Acceptance criteria

- [x] Human docs no longer imply the CLI automatically offers to save reports.
- [x] Human docs pass the documentation-separation grep for `memory-bank`, `task 0`, and `.cursor`.
- [x] Task 0027 and task 0035 metadata are aligned with `INDEX.md`.
- [x] `activeContext.md` and `progress.md` reflect final task status.
- [x] `python -m retail_agent.evals` passes.
- [x] Changes are committed.

## References

- `docs/TECHNICAL_EXPLANATION.md`
- `memory-bank/tasks/0027-golden-learning-hardening/TASK.md`
- `memory-bank/tasks/0035-final-reviewer-docs-evidence-polish/TASK.md`
