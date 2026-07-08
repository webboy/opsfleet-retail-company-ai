# Active Context

## Current focus

Full assignment review pass (2026-07-08, reviewer stance against `docs/AI Technical Assignment - Retail Company.pdf`) produced new backlog tasks **0022–0027**. Tasks **0016** through **0022** are **done** (user approved 2026-07-08); task **0023** is **pending_review**; tasks **0024–0027** are **todo**.

Review backlog (created 2026-07-08):

1. **0022 (high)** — ~~SQL cost controls and MCP payload caps~~ — **done** (user approved 2026-07-08): clamp oversized explicit `LIMIT`, cap MCP rows.
2. **0023 (high)** — ~~input guard structured labels~~ — **pending_review**: replace brittle substring label parsing.
3. **0024 (high)** — empty results and live eval regression: avoid full retry loops on valid empty results; investigate `cancelled-order-rate` live fallback.
4. **0025 (medium/high)** — CI and eval gate hardening: add enforceable local/CI gate and clarify dry-run vs live eval.
5. **0026 (medium)** — submission docs alignment: remove dataset/docs overclaims and improve reviewer-facing capability/schema/eval docs.
6. **0027 (medium)** — Golden Bucket and learning-loop hardening: avoid arbitrary no-overlap trios and incomplete candidate captures.

Second-pass confirmed bugs (each reproduced; details in the task folders):

1. **0017 (high)** — ~~PII marker over-match~~ — **done** (user approved 2026-07-08): token-boundary matching + numeric metric exemption; live CLI verified (`Masked PII columns=[]`).
2. **0018 (medium)** — ~~`/save` persists non-analysis output~~ — **done** (user approved 2026-07-08): `last_analysis_*` state + graph regression tests.
3. **0019 (medium)** — ~~malformed trio file crashes CLI~~ — **done** (user approved 2026-07-08): skip-and-warn in `load_trios`.
4. **0020 (medium)** — ~~preference regex hijacks analysis~~ — **done** (user approved 2026-07-08): formatting-intent patterns + DB-table guard.
5. **0021 (low)** — ~~eval `--layer` phantom regressions, inflated `self_heal_events`, stale trace fields, `.env` precedence~~ — **done** (user approved 2026-07-08).

First-pass status: ~~0012~~ ~~0013~~ ~~0014~~ ~~0015~~ ~~0016~~ ~~0017~~ ~~0018~~ ~~0019~~ ~~0020~~ ~~0021~~ — **done** (user approved 2026-07-08).

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

- Task 0022 should decide whether `default_limit` is also the hard maximum or whether a separate max/result cap setting is clearer. **Resolved:** `BQ_DEFAULT_LIMIT` is the SQL hard max; `MCP_MAX_RESPONSE_ROWS` is a separate MCP payload cap (default 100).
- Task 0024 needs live-eval evidence if credentials are available; dry-run alone does not prove the `cancelled-order-rate` fix.
- Live eval judge scores may vary; dry-run baseline is committed for CI-stable regression checks.
- Preference phrase detection is deterministic; edge phrasing may need expansion over time.
- README transcripts are curated; spot-check with live chat recommended before final demo.

## Recent changes

- 2026-07-08: Task 0023 **pending_review** — exact LLM guard label parsing + regressions; version **0.21.0**.
- 2026-07-08: Task 0022 **done** (user approved) — SQL LIMIT clamping + MCP response row cap (`MCP_MAX_RESPONSE_ROWS`); version **0.20.0**.
- 2026-07-08: Task 0022 **pending_review** — SQL LIMIT clamping + MCP response row cap (`MCP_MAX_RESPONSE_ROWS`); version **0.20.0**.
- 2026-07-08: Task 0021 **done** (user approved) — eval layer baseline filter, per-turn self-heal metric, trace snapshot guard, env precedence; version **0.19.0**.
- 2026-07-08: Task 0021 **pending_review** — eval layer baseline filter, per-turn self-heal metric, trace snapshot guard, env precedence; version **0.19.0**; pytest 189, dry-run eval 16/16, safety subset 5/5.
- 2026-07-08: Task 0020 **pending_review** — preference detection requires formatting intent; version **0.18.0**; pytest 183, dry-run eval 16/16.
- 2026-07-08: Task 0019 **done** (user approved) — skip malformed trio files with warning; version **0.17.0**.
- 2026-07-08: Task 0019 **pending_review** — skip malformed trio files with warning; version **0.17.0**; pytest 175, dry-run eval 16/16.
- 2026-07-08: Task 0018 **done** (user approved) — `/save` uses `last_analysis_*` fields; version **0.16.0**.
- 2026-07-08: Task 0018 **pending_review** — `/save` uses `last_analysis_*` fields; graph regression tests; version **0.16.0**; pytest 170, dry-run eval 16/16.
- 2026-07-08: Task 0017 **done** (user approved) — token-boundary PII column matching + numeric metric exemption; live CLI verified; version **0.15.0**.
- 2026-07-08: Task 0017 **pending_review** — token-boundary PII column matching + numeric metric exemption; graph regression test; version **0.15.0**; pytest 167, dry-run eval 16/16.
- 2026-07-08: Second deep-review pass — created tasks 0017–0021; verified 0012–0015 fixes live (CTE on BigQuery, 10-turn budget, cross-user delete scope, confirm-variant cancels, MCP stdio, eval flags); pytest 157, dry-run eval 16/16; `.env` on Ollama-primary + Gemini-fallback confirmed working in live CLI.
- 2026-07-08: Task 0016 **done** (user approved) — CLI diagnostics gated to analysis turns; eval/docs polish; version **0.14.0**.
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
