# Active Context

## Current focus

Task **0011** (LLM provider fallback) is **done** (user approved 2026-07-07). Next up: task **0008** (observability/QA evals).

## How work is organized

- All implementation work happens through **task folders** in `memory-bank/tasks/` — see `.cursor/rules/task-folder-workflow.mdc`, `task-index-workflow.mdc`, `task-quality-lifecycle.mdc`, `memory-task-minor-version-bump.mdc`, `task-execution-commit-required.mdc`.
- The Engineer agent must read the whole memory bank first, then open the next `todo` task in `INDEX.md`, refine its `PLAN.md`, implement, test, commit (Conventional Commits), and set the task to `pending_review`. Only the user promotes tasks to `done`.

## Active decisions (see systemPatterns.md for full ADRs)

- LangGraph + configurable LLM providers: Gemini (default), OpenRouter, Ollama via `create_chat_model()`; optional fallback on quota/outage (task 0011).
- Safety is deterministic: `input_guard` (scope/injection/off-topic), `sql_guard` (SELECT-only, allowed tables, LIMIT, bytes cap), and `pii_mask` + `output_mask` (column deny-list + regex sweep) are code, not prompts.
- Saved reports and user preferences: SQLite via `RETAIL_AGENT_DB_PATH`; delete uses LangGraph `interrupt()` with owner-scoped selectors.
- Personas: hot-read from `personas/` (`RETAIL_AGENT_PERSONAS_DIR`); `/persona` is session-only override.
- Golden Bucket prototype = local trio files under `golden_bucket/` + Gemini embedding retrieval with keyword fallback.
- **Maximum-effort scope (user decision, 2026-07-07)**: the prototype implements **all five** optional requirements as first-class features.
- **Documentation separation (user decision, 2026-07-07)**: `README.md` + `docs/` are human-facing; `memory-bank/` is internal agent documentation.

## Open questions / risks

- Gemini free-tier rate limits during development — mitigated by call caps, alternate models, and task 0011 fallback provider.
- BigQuery auth on the reviewer's machine is the most fragile setup step — README must cover it carefully (task 0009).
- Preference phrase detection is deterministic; edge phrasing may need expansion over time.
- Fallback provider model quality may differ from Gemini — monitor during evals (task 0008).

## Recent changes

- 2026-07-07 (evening): **Product lens adopted** (user shared recruiter feedback: winning take-homes start from a user moment and build backwards; features ≠ workflows). Changes: `productContext.md` new "Product lens" section; `compose_report` system prompt now demands answer-first, decision-guiding reports; task 0008 judge rubric scores decision-usefulness; task 0009 README transcripts restructured as one continuous manager workflow story instead of isolated feature demos.

- 2026-07-07: Task 0011 **done** (user approved) — LLM provider factory + OpenRouter/Ollama fallback, version **0.7.0**.
- 2026-07-07: Task 0007 **done** (user approved) — user preferences, hot-reload personas, version **0.6.0**.
- 2026-07-07: Tasks 0001–0006 **done** (user approved).
