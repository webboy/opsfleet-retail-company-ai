# Active Context

## Current focus

Task **0008** (observability & QA eval suite) is **pending_review** — implementation complete, awaiting user testing/approval. Next after approval: task **0009** (final documentation & submission polish).

## How work is organized

- All implementation work happens through **task folders** in `memory-bank/tasks/` — see `.cursor/rules/task-folder-workflow.mdc`, `task-index-workflow.mdc`, `task-quality-lifecycle.mdc`, `memory-task-minor-version-bump.mdc`, `task-execution-commit-required.mdc`.
- The Engineer agent must read the whole memory bank first, then open the next `todo` task in `INDEX.md`, refine its `PLAN.md`, implement, test, commit (Conventional Commits), and set the task to `pending_review`. Only the user promotes tasks to `done`.

## Active decisions (see systemPatterns.md for full ADRs)

- LangGraph + configurable LLM providers: Gemini (default), OpenRouter, Ollama via `create_chat_model()`; optional fallback on quota/outage (task 0011).
- Observability: per-node JSONL events via `TurnTracer`; `trace` and `metrics` CLIs; optional LangSmith via env.
- QA eval gate: `evals/cases.yaml` + dry-run-first runner; LLM-as-judge for intent scoring; baseline at `evals/baseline/dry-run-v0.8.0.jsonl`.
- Safety is deterministic: `input_guard`, `sql_guard`, `pii_mask` + `output_mask` are code, not prompts.
- Saved reports and user preferences: SQLite via `RETAIL_AGENT_DB_PATH`; delete uses LangGraph `interrupt()`.
- Personas: hot-read from `personas/`; `/persona` is session-only override.
- Golden Bucket prototype = local trio files + embedding retrieval with keyword fallback.
- **Maximum-effort scope (user decision, 2026-07-07)**: the prototype implements **all five** optional requirements as first-class features.
- **Documentation separation (user decision, 2026-07-07)**: `README.md` + `docs/` are human-facing; `memory-bank/` is internal agent documentation.

## Open questions / risks

- BigQuery auth on the reviewer's machine is the most fragile setup step — README must cover it carefully (task 0009).
- Live eval judge scores may vary; dry-run baseline is committed for CI-stable regression checks.
- Preference phrase detection is deterministic; edge phrasing may need expansion over time.

## Recent changes

- 2026-07-07: Task 0008 **pending_review** — observability JSONL tracing, trace/metrics CLIs, eval suite, version **0.8.0**, **118 pytest passed**.
- 2026-07-07: Task 0011 **done** (user approved) — LLM provider factory + fallback, version **0.7.0**.
- 2026-07-07: Tasks 0001–0007 **done** (user approved).
