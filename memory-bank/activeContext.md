# Active Context

## Current focus

Full-code review (2026-07-08) against the assignment PDF produced five new bug-fix tasks **0012–0016** (all `todo`). Task **0010** (optional MCP server) remains **pending_review**. All core tasks 0001–0009 and 0011 are **done**.

Review-confirmed bugs (each reproduced; details in the task folders):

1. ~~**0012**~~ — CTE support in `sql_guard` — **done** (user approved 2026-07-08).
2. ~~**0013**~~ — per-turn LLM budget reset — **done** (user approved 2026-07-08).
3. **0014** — name-flagged PII columns leak unformatted values (`phone` = `5551234567` passes unmasked).
4. **0015** — connection-level LLM outages (refused/DNS/timeout) bypass retry and never reach the configured fallback provider.
5. **0016** — CLI prints stale `[sql attempts]`/`[retrieved trios]` after save/list/prefs turns; docs test-count drift (120/131 vs actual 132); brittle live eval token (`denim`).

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
- **Submission docs (task 0009)**: README is reviewer entry point; USAGE + EVALUATION complete the `docs/` package.
- **MCP stretch (task 0010)**: optional `retail-agent-mcp` stdio server; `docs/MCP.md`; version **0.9.0**.

## Open questions / risks

- Live eval judge scores may vary; dry-run baseline is committed for CI-stable regression checks.
- Preference phrase detection is deterministic; edge phrasing may need expansion over time.
- README transcripts are curated; spot-check with live chat recommended before final demo.

## Recent changes

- 2026-07-08: Task 0012 **done** (user approved) — CTE aliases in `sql_guard`; live BQ verified.
- 2026-07-08: Task 0012 **pending_review** — CTE aliases allowed in `sql_guard`; 4 regression tests; live BQ verified; version **0.11.0**.
- 2026-07-08: Task 0013 **pending_review** — `input_guard` resets LLM budget per turn; regression test; version **0.10.0**.
- 2026-07-08: Task 0010 **pending_review** — MCP server (`query_retail_data`, `retrieve_trios`), handler tests, `docs/MCP.md`, version **0.9.0**; 131 pytest, 16/16 eval.
- 2026-07-08: Task 0009 **done** (user approved) — submission README, USAGE, EVALUATION, architecture drift fixes.
- 2026-07-08: Task 0009 **pending_review** — full README, USAGE, EVALUATION, architecture/technical drift fixes, fresh venv verified (120 pytest, 16 eval).
- 2026-07-08: Task 0008 **done** (user approved) — observability JSONL tracing, trace/metrics CLIs, eval suite, version **0.8.0**.
- 2026-07-07: Task 0011 **done** (user approved) — LLM provider factory + fallback, version **0.7.0**.
