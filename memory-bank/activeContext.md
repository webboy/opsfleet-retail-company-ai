# Active Context

## Current focus

Second deep-review pass (2026-07-08, strict edge-case testing) produced five new tasks **0017–0021** (all `todo`). Task **0016** polish remains **pending_review**. First-pass fixes 0012–0015 verified working in this pass (CTE live on BigQuery, 10-turn budget reset, ownership-scoped deletes, MCP stdio handshake).

Second-pass confirmed bugs (each reproduced; details in the task folders):

1. **0017 (high)** — PII marker over-match: `"cell"` substring flags `cancelled_rate` etc.; after 0014's unconditional masking, legit metrics reach the report LLM as `***` (proven end-to-end). Dry-run evals are blind to it.
2. **0018 (medium)** — `/save` persists the latest answer of *any* turn (preference confirmations, list output, refusals) instead of the last analysis report.
3. **0019 (medium)** — one malformed `golden_bucket/*.md` file crashes CLI startup with a raw traceback.
4. **0020 (medium)** — preference regex hijacks analysis questions like "Can I use the orders table to compute revenue?" and corrupts the stored preference.
5. **0021 (low)** — eval `--layer` subsets exit 1 with phantom baseline regressions; `self_heal_events` inflated (counts node events, not turns); node events carry stale cross-turn SQL/trios; `.env` overrides shell env vars (`override=True`).

First-pass status: ~~0012~~ ~~0013~~ ~~0014~~ ~~0015~~ — **done** (user approved 2026-07-08); **0016** — **pending_review**.

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

- 2026-07-08: Second deep-review pass — created tasks 0017–0021; verified 0012–0015 fixes live (CTE on BigQuery, 10-turn budget, cross-user delete scope, confirm-variant cancels, MCP stdio, eval flags); pytest 157, dry-run eval 16/16; `.env` on Ollama-primary + Gemini-fallback confirmed working in live CLI.
- 2026-07-08: Task 0016 **pending_review** — CLI diagnostics gated to analysis turns; eval/docs polish; version **0.14.0**.
- 2026-07-08: Task 0015 **done** (user approved) — connection-level LLM outage classification + immediate fallback; live Ollama CLI verified; version **0.13.0**.
- 2026-07-08: Task 0015 **pending_review** — connection-level LLM outage classification + immediate fallback; version **0.13.0**.
- 2026-07-08: Task 0014 **done** (user approved) — strict name-flagged PII column masking; version **0.12.0**.
- 2026-07-08: Task 0014 **pending_review** — strict name-flagged PII column masking; unformatted phones masked; version **0.12.0**.
- 2026-07-08: Task 0012 **done** (user approved) — CTE aliases in `sql_guard`; live BQ verified.
- 2026-07-08: Task 0012 **pending_review** — CTE aliases allowed in `sql_guard`; 4 regression tests; live BQ verified; version **0.11.0**.
- 2026-07-08: Task 0013 **pending_review** — `input_guard` resets LLM budget per turn; regression test; version **0.10.0**.
- 2026-07-08: Task 0010 **done** (user approved) — MCP server (`query_retail_data`, `retrieve_trios`), `docs/MCP.md`, version **0.9.0**.
- 2026-07-08: Task 0010 **pending_review** — MCP server (`query_retail_data`, `retrieve_trios`), handler tests, `docs/MCP.md`, version **0.9.0**; 131 pytest, 16/16 eval.
- 2026-07-08: Task 0009 **done** (user approved) — submission README, USAGE, EVALUATION, architecture drift fixes.
- 2026-07-08: Task 0009 **pending_review** — full README, USAGE, EVALUATION, architecture/technical drift fixes, fresh venv verified (120 pytest, 16 eval).
- 2026-07-08: Task 0008 **done** (user approved) — observability JSONL tracing, trace/metrics CLIs, eval suite, version **0.8.0**.
- 2026-07-07: Task 0011 **done** (user approved) — LLM provider factory + fallback, version **0.7.0**.
