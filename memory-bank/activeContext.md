# Active Context

## Current focus

Final assignment polish is complete (2026-07-08). Tasks **0001–0036** are **done** after the final review cleanup and user approval/instruction.

Review backlog (created 2026-07-08):

1. **0022 (high)** — ~~SQL cost controls and MCP payload caps~~ — **done** (user approved 2026-07-08): clamp oversized explicit `LIMIT`, cap MCP rows.
2. **0023 (high)** — ~~input guard structured labels~~ — **done** (user approved 2026-07-08): replace brittle substring label parsing.
3. **0024 (high)** — ~~empty results and live eval regression~~ — **done** (user approved 2026-07-08): valid empty results report without retry; eval failure diagnostics; version **0.22.0**.
4. **0025 (medium/high)** — ~~CI and eval gate hardening~~ — **done** (user approved 2026-07-08): GitHub Actions `pytest` + dry-run eval; docs clarify dry-run vs live.
5. **0026 (medium)** — ~~submission docs alignment~~ — **done** (user approved 2026-07-08): `docs/SCHEMA.md`, dataset-faithful examples, eval/setup drift fixes.
6. **0027 (medium)** — ~~Golden Bucket and learning-loop hardening~~ — **done** (user approved 2026-07-08): zero-overlap keyword fallback, `report_complete` capture gating, version **0.23.0**.
7. **0028 (medium)** — ~~Golden embedding relevance~~ — **done** (user instruction: mark done when tests pass): embedding similarity floor, version **0.24.0**.
8. **0029 (medium)** — ~~Save complete report gating~~ — **done** (user instruction: mark done when tests pass): `/save` only persists complete analysis reports; version **0.25.0**.
9. **0030 (medium)** — ~~Input guard fail-closed fallback~~ — **done** (user instruction: mark done when tests pass): malformed classifier output routes to `off_topic`; version **0.26.0**.
10. **0031 (low)** — ~~Reviewer docs polish~~ — **done** (user instruction: mark done when checks pass): clone URL, CLI-accurate examples, delete-by-today evidence, production data-flow label, MIT LICENSE.
11. **0032 (medium)** — ~~Live QA evidence hardening~~ — **done** (user instruction: mark done when tests pass): judge tests, `--require-judge`, empty-result eval case, live limitation docs; version **0.27.0**.
12. **0033 (medium)** — ~~Input guard classify-unavailable fail-closed~~ — **done** (user instruction: mark done when tests pass): budget/quota classify-skip fails closed for ambiguous input; version **0.28.0**.
13. **0034 (medium)** — ~~Golden keyword fallback relevance floor~~ — **done** (user instruction: mark done when tests pass): minimum shared-token floor for keyword fallback; version **0.29.0**.
14. **0035 (low)** — ~~Final reviewer docs and evidence polish~~ — **done** (user approved 2026-07-08): save-flow drift, complete-report gating docs, assignment phrasing, golden env vars, sanitized live eval table; docs-only.
15. **0036 (low)** — ~~Final metadata and doc sync~~ — **done**: stale save-flow sentence removed; task metadata synchronized and committed.

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
- Live eval with Ollama primary: capability layer **9/11** with `--no-judge` when settings/credentials OK; remaining live failures are NL-to-SQL quality (e.g. `cancelled-order-rate`), not empty-result routing. Shell env overrides `.env` — verify provider before live runs.
- Live eval judge scores may vary; dry-run baseline is committed for CI-stable regression checks.
- Preference phrase detection is deterministic; edge phrasing may need expansion over time.
- README transcripts are curated; spot-check with live chat recommended before final demo.
- No active open task. Final reviewer polish and metadata sync are complete.

## Recent changes

- Task 0036 **done** — final metadata/doc sync: removed stale automatic save-prompt wording and aligned tasks 0027/0035/INDEX/progress; dry-run eval 17/17.
- Task 0035 **done** — reviewer docs polish: save-flow drift fix, complete-report gating in USAGE/TECHNICAL, assignment phrasing, golden env vars, sanitized live eval table; dry-run eval 17/17.
- Task 0034 **done** — keyword fallback relevance floor (`GOLDEN_KEYWORD_MIN_OVERLAP`, default 2); version **0.29.0**; pytest 236, dry-run eval 17/17.
- Task 0033 **done** — input guard classify-unavailable fail-closed: budget/quota classify-skip refuses ambiguous input; version **0.28.0**; pytest 235, dry-run eval 17/17.
- Task 0032 **done** — live QA evidence hardening: judge tests, `--require-judge`, `valid-empty-result` eval case, cancelled-order live weakness docs; version **0.27.0**; pytest 232, dry-run eval 17/17.
- 2026-07-08: Task 0031 **done** — reviewer docs polish (clone URL, CLI-accurate examples, delete-by-today, production data-flow label, MIT LICENSE); dry-run eval 16/16.
- 2026-07-08: Task 0030 **done** — input guard fail-closed fallback to `off_topic` for malformed classifier output; version **0.26.0**; pytest 226, safety eval 5/5, dry-run eval 16/16.
- 2026-07-08: Task 0029 **done** — `/save` gated on `last_analysis_complete`; incomplete compose/fallback no longer populates saveable state; version **0.25.0**; pytest 225, dry-run eval 16/16.
- 2026-07-08: Task 0028 **done** — embedding similarity threshold (`GOLDEN_EMBEDDING_MIN_SIMILARITY`, default 0.35); version **0.24.0**; pytest 221, dry-run eval 16/16.
- 2026-07-08: Task 0027 **done** (user approved) — zero-overlap keyword fallback, `report_complete` capture gating; version **0.23.0**; pytest 219, dry-run eval 16/16.
- 2026-07-08: Task 0026 **done** (user approved) — `docs/SCHEMA.md`, submission doc alignment (no version bump); dry-run eval 16/16.
- 2026-07-08: Task 0026 **pending_review** — `docs/SCHEMA.md`, submission doc alignment (no version bump); dry-run eval 16/16.
- 2026-07-08: Task 0025 **done** (user approved) — GitHub Actions CI (`pytest` + dry-run eval); eval/README docs for dry-run vs live.
- 2026-07-08: Task 0024 **pending_review** — empty-result routing fix, eval diagnostics, regressions; version **0.22.0**; pytest 212, dry-run eval 16/16, live eval 14/16.
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
