# Active Context

## Current focus

Task **0004** (Golden Bucket trio retrieval) is **pending_review** — implementation complete, awaiting user verification. Next after approval: task **0005** (input guard + PII masking).

## How work is organized

- All implementation work happens through **task folders** in `memory-bank/tasks/` — see `.cursor/rules/task-folder-workflow.mdc`, `task-index-workflow.mdc`, `task-quality-lifecycle.mdc`, `memory-task-minor-version-bump.mdc`.
- The Engineer agent must read the whole memory bank first, then open the next `todo` task in `INDEX.md`, refine its `PLAN.md`, implement, test, commit (Conventional Commits), and set the task to `pending_review`. Only the user promotes tasks to `done`.

## Active decisions (see systemPatterns.md for full ADRs)

- LangGraph + Gemini (`gemini-2.5-flash` default, env-configurable), optional OpenRouter/Ollama fallback.
- Safety is deterministic: sql_guard (SELECT-only, allowed tables, LIMIT, bytes cap) and pii_mask (column deny-list + regex sweep) are code, not prompts.
- Delete confirmations use LangGraph `interrupt()`; reports are owner-scoped in SQLite.
- Golden Bucket prototype = local trio files under `golden_bucket/` + Gemini embedding retrieval with keyword fallback; candidates in `golden_bucket/candidates/candidates.jsonl`.
- Personas = hot-read text files; user prefs = SQLite; observability = structured JSONL events + optional LangSmith.
- **Maximum-effort scope (user decision, 2026-07-07)**: the prototype implements **all five** optional requirements as first-class features (PII Masking, High-Stakes Oversight, Resilience, QA, Observability). QA is a full eval suite with intent-correctness scoring (LLM-as-judge on top of property assertions), not just a smoke set.
- **Documentation separation (user decision, 2026-07-07)**: `README.md` + `docs/` are human-facing and self-contained (the assignment's Documentation deliverable); `memory-bank/` is internal agent documentation. Human docs must never reference memory-bank, tasks or agent workflow — enforced by `.cursor/rules/documentation-separation.mdc` and audited in task 0009.

## Open questions / risks

- Gemini free-tier rate limits during development — mitigate with call caps and small prompts; OpenRouter fallback if blocked.
- BigQuery auth on the reviewer's machine is the most fragile setup step — README must cover it carefully (task 0009).
- Resolved (2026-07-07): `memory-bank/` and `.cursor/` **are committed** to the repo — the user wants clones on other machines to carry the full agent context. The Memory Bank usage rule was moved from Cursor global user rules into the project (`.cursor/rules/memory-bank.mdc`) so any clone self-describes the workflow. Final pre-submission sweep (no secrets, tidy worklogs) remains part of task 0009.
- The assignment states a 6–12 h expectation, but the user has chosen a maximum-effort submission: full coverage of all five optional prototype requirements takes priority over staying inside that budget. Still: no speculative abstractions — depth goes into requirement coverage and polish, not framework-building.

## Recent changes

- 2026-07-07: Task 0004 **pending_review** — Golden Bucket: 10 seed trios, `golden.py`, retrieve/inject/capture graph nodes, 41 pytest passed, version **0.3.0**.
- 2026-07-07: Task 0003 **done** (user approved) — LangGraph agent core, CLI REPL, self-heal; follow-up fix for greetings/invalid SQL guard.
- 2026-07-07: Task 0001 **done** (user approved) — `docs/ARCHITECTURE.md` and `docs/TECHNICAL_EXPLANATION.md`.
