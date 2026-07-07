# Active Context

## Current focus

Task **0005** (input guard + PII masking) is **pending_review** — implementation complete, awaiting user verification. Next after approval: task **0006** (saved reports + delete confirmation).

## How work is organized

- All implementation work happens through **task folders** in `memory-bank/tasks/` — see `.cursor/rules/task-folder-workflow.mdc`, `task-index-workflow.mdc`, `task-quality-lifecycle.mdc`, `memory-task-minor-version-bump.mdc`, `task-execution-commit-required.mdc`.
- The Engineer agent must read the whole memory bank first, then open the next `todo` task in `INDEX.md`, refine its `PLAN.md`, implement, test, commit (Conventional Commits), and set the task to `pending_review`. Only the user promotes tasks to `done`.

## Active decisions (see systemPatterns.md for full ADRs)

- LangGraph + Gemini (`gemini-2.5-flash` default, env-configurable), optional OpenRouter/Ollama fallback.
- Safety is deterministic: `input_guard` (scope/injection/off-topic), `sql_guard` (SELECT-only, allowed tables, LIMIT, bytes cap), and `pii_mask` + `output_mask` (column deny-list + regex sweep) are code, not prompts.
- Explicit PII requests may run as analysis but output is always masked with a policy note.
- Delete confirmations use LangGraph `interrupt()`; reports are owner-scoped in SQLite (task 0006).
- Golden Bucket prototype = local trio files under `golden_bucket/` + Gemini embedding retrieval with keyword fallback.
- Personas = hot-read text files; user prefs = SQLite; observability = structured JSONL events + optional LangSmith.
- **Maximum-effort scope (user decision, 2026-07-07)**: the prototype implements **all five** optional requirements as first-class features.
- **Documentation separation (user decision, 2026-07-07)**: `README.md` + `docs/` are human-facing; `memory-bank/` is internal agent documentation.

## Open questions / risks

- Gemini free-tier rate limits during development — mitigate with call caps and small prompts.
- BigQuery auth on the reviewer's machine is the most fragile setup step — README must cover it carefully (task 0009).
- LLM guard fallback may misclassify edge cases; deterministic rules handle obvious malicious/off-topic inputs first.

## Recent changes

- 2026-07-07: Task 0005 **pending_review** — input guard, PII masking, 54 pytest passed, version **0.4.0**.
- 2026-07-07: Task 0004 **done** — Golden Bucket trio retrieval and candidate capture.
- 2026-07-07: Schema doc aligned with live BigQuery (`order_items.id` not `order_item_id`).
