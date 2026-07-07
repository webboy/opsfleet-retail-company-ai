# Active Context

## Current focus

Project bootstrap is done (2026-07-07): assignment analyzed, memory bank initialized, task workflow rules adapted into `.cursor/rules/`, and the task backlog created in `memory-bank/tasks/`. The workflow for any implementing agent is fully described by the memory bank plus the rules in `.cursor/rules/` — read the memory bank first, then work through `memory-bank/tasks/INDEX.md` in order.

**Next up: task `0001-docs-hld-architecture`** — the HLD and technical explanation are the highest-weighted deliverable, and writing them first locks the design the code must follow. After that, tasks 0002 → 0009 in order (see `memory-bank/tasks/INDEX.md`).

## How work is organized

- All implementation work happens through **task folders** in `memory-bank/tasks/` — see `.cursor/rules/task-folder-workflow.mdc`, `task-index-workflow.mdc`, `task-quality-lifecycle.mdc`, `memory-task-minor-version-bump.mdc`.
- The Engineer agent must read the whole memory bank first, then open the next `todo` task in `INDEX.md`, refine its `PLAN.md`, implement, test, commit (Conventional Commits), and set the task to `pending_review`. Only the user promotes tasks to `done`.

## Active decisions (see systemPatterns.md for full ADRs)

- LangGraph + Gemini (`gemini-2.5-flash` default, env-configurable), optional OpenRouter/Ollama fallback.
- Safety is deterministic: sql_guard (SELECT-only, allowed tables, LIMIT, bytes cap) and pii_mask (column deny-list + regex sweep) are code, not prompts.
- Delete confirmations use LangGraph `interrupt()`; reports are owner-scoped in SQLite.
- Golden Bucket prototype = local trio files + embedding retrieval with keyword fallback.
- Personas = hot-read text files; user prefs = SQLite; observability = structured JSONL events + optional LangSmith.
- **Maximum-effort scope (user decision, 2026-07-07)**: the prototype implements **all five** optional requirements as first-class features (PII Masking, High-Stakes Oversight, Resilience, QA, Observability). QA is a full eval suite with intent-correctness scoring (LLM-as-judge on top of property assertions), not just a smoke set.
- **Documentation separation (user decision, 2026-07-07)**: `README.md` + `docs/` are human-facing and self-contained (the assignment's Documentation deliverable); `memory-bank/` is internal agent documentation. Human docs must never reference memory-bank, tasks or agent workflow — enforced by `.cursor/rules/documentation-separation.mdc` and audited in task 0009.

## Open questions / risks

- Gemini free-tier rate limits during development — mitigate with call caps and small prompts; OpenRouter fallback if blocked.
- BigQuery auth on the reviewer's machine is the most fragile setup step — README must cover it carefully (task 0009).
- Resolved (2026-07-07): `memory-bank/` and `.cursor/` **are committed** to the repo — the user wants clones on other machines to carry the full agent context. The Memory Bank usage rule was moved from Cursor global user rules into the project (`.cursor/rules/memory-bank.mdc`) so any clone self-describes the workflow. Final pre-submission sweep (no secrets, tidy worklogs) remains part of task 0009.
- The assignment states a 6–12 h expectation, but the user has chosen a maximum-effort submission: full coverage of all five optional prototype requirements takes priority over staying inside that budget. Still: no speculative abstractions — depth goes into requirement coverage and polish, not framework-building.

## Recent changes

- 2026-07-07: repo bootstrapped (memory bank, rules, task backlog). No application code yet.
- 2026-07-07: scope raised to maximum effort — all five optional prototype requirements are in scope as first-class features; task 0008 QA scope expanded accordingly.
