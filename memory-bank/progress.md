# Progress

## Status snapshot (2026-07-08)

Tasks 0001–0009, **0010**, **0011**, **0012**, **0013**, **0014**, **0015**, **0016**, **0017**, **0018**, **0019**, **0020**, **0021**, **0022**, **0023**, **0024**, **0025**, **0026**, **0028**, **0029**, **0030**, **0031**, **0032**, **0033**, and **0034** **done** (user approved or per-task instruction). Task **0027** is **pending_review**.

## What works

- Memory bank initialized and task workflow rules in `.cursor/rules/`.
- Production HLD + technical explanation in `docs/` (task 0001, **done**).
- Agent core: LangGraph SQL self-heal + CLI (task 0003, **done**).
- Golden Bucket: trio retrieval, prompt injection, candidate capture (task 0004, **done**).
- Safety: input guard, DataFrame PII mask, output sweep + policy note (task 0005, **done**).
- Saved reports: SQLite store, save/list/delete with interrupt confirmation (task 0006, **done**).
- User preferences + personas: SQLite prefs, deterministic routing, hot-reload persona files (task 0007, **done**).
- LLM provider factory: Gemini, OpenRouter, Ollama with optional fallback (task 0011, **done**).
- Observability: per-node JSONL events, `trace`/`metrics` CLIs (task 0008, **done**).
- QA eval suite: 17 cases, dry-run default, judge scoring, baseline regression (task 0008 + 0032, **done**).
- **Human docs package**: README, USAGE, EVALUATION, drift-corrected architecture/technical (task 0009, **done**).
- **Optional MCP server**: `retail-agent-mcp`, guarded `query_retail_data` + `retrieve_trios` (task 0010, **done**).
- `pytest` **236 passed**; eval dry-run **17/17 passed**; safety subset **5/5 passed**.
- **Golden keyword fallback relevance floor** (task 0034, **done**): minimum shared-token count for keyword fallback; version **0.29.0**.
- **Input guard classify-unavailable fail-closed** (task 0033, **done**): budget/quota classify-skip refuses ambiguous input; version **0.28.0**.
- **Live QA evidence hardening** (task 0032, **done**): judge low-score/unavailable tests, `--require-judge`, `valid-empty-result` eval case, cancelled-order live weakness docs; version **0.27.0**.
- **Input guard fail-closed fallback** (task 0030, **done**): malformed classifier output routes to `off_topic`; version **0.26.0**.
- **Reviewer docs polish** (task 0031, **done**): clone URL, CLI-accurate example transcripts, delete-by-today examples, production data-flow label, MIT LICENSE.
- **Save complete report gating** (task 0029, **done**): `/save` only persists complete analysis reports; version **0.25.0**.
- **Golden embedding relevance** (task 0028, **done**): cosine similarity floor for embedding retrieval; version **0.24.0**.
- **Empty-result routing** (task 0024, **done**): valid zero-row queries report without retry; eval failure diagnostics; dry-run regressions; live eval diagnostics verified.
- **SQL LIMIT clamping and MCP payload caps** (task 0022, **done**): explicit oversized limits clamped; MCP responses capped via `MCP_MAX_RESPONSE_ROWS`.
- **Input guard structured labels** (task 0023, **done**): exact first-line/JSON LLM label parsing with `analysis` fallback.
- **LLM budget per-turn reset** (task 0013, **done**): `input_guard` uses `fresh_budget`; 6-turn regression test; live CLI verified.
- **CTE support in sql_guard** (task 0012, **done**): bare CTE aliases allowed; 4 regression tests; live BQ verified.
- **Name-flagged PII column masking** (task 0014, **done**): unformatted phones and arbitrary strings masked in PII-named columns; content-detected path unchanged.
- **LLM connection-outage resilience** (task 0015, **done**): connection errors classify as transient; immediate fallback when configured.
- **CLI/docs/eval polish** (task 0016, **done**): analysis-only diagnostics; property-based live eval tokens; docs count drift removed.
- **PII marker token matching** (task 0017, **done**): metric columns like `cancelled_rate`/`email_count` no longer falsely masked; string PII columns still strictly masked.
- **Save last analysis report** (task 0018, **done**): `/save` uses `last_analysis_*` instead of latest turn answer.
- **Golden Bucket robust loading** (task 0019, **done**): malformed trio files skipped with warning; CLI/MCP keep running.
- **Preference formatting intent** (task 0020, **done**): DB-table analysis questions no longer hijack preference routing.
- **CI gate** (task 0025, **done**): GitHub Actions runs `pytest -q` + dry-run eval; docs clarify dry-run vs live.
- **Submission docs alignment** (task 0026, **done**): `docs/SCHEMA.md`, supported-question matrix, dataset boundaries, eval/setup drift fixes.
- **Golden Bucket hardening** (task 0027, **pending_review**): zero-overlap keyword fallback, `report_complete` capture gating; version **0.23.0**.

1. ~~`0001`–`0009`, `0011`~~ — **done**
2. ~~`0010` *(optional)* MCP server~~ — **done**
3. ~~`0012` CTE sql_guard~~ — **done**
4. ~~`0014` PII name-flagged masking~~ — **done**
5. ~~`0015` LLM connection resilience~~ — **done**
6. ~~`0016` CLI/docs/eval polish~~ — **done**
7. ~~`0013` LLM budget reset~~ — **done**
8. ~~`0017` PII marker over-match~~ — **done**
9. ~~`0018` `/save` scope fix~~ — **done**
10. ~~`0019` Golden Bucket robust loading~~ — **done**
11. ~~`0020` preference regex tightening~~ — **done**
12. ~~`0021` tooling polish~~ — **done**
13. ~~`0022` SQL cost controls and MCP payload caps~~ — **done**
14. ~~`0023` Input guard structured labels~~ — **done**
15. ~~`0024` Empty results and live eval regression~~ — **done**
16. ~~`0025` CI and eval gate hardening~~ — **done**
17. ~~`0026` Submission docs alignment~~ — **done**
18. `0027` Golden Bucket and learning-loop hardening — **pending_review**
19. ~~`0028` Golden embedding relevance~~ — **done**
20. ~~`0029` Save complete report gating~~ — **done**
21. ~~`0030` Input guard fail-closed fallback~~ — **done**
22. ~~`0031` Reviewer docs polish~~ — **done**
23. ~~`0032` Live QA evidence hardening~~ — **done**
24. ~~`0033` Input guard classify-unavailable fail-closed~~ — **done**
25. ~~`0034` Golden keyword fallback relevance floor~~ — **done**

## Known issues

- ~~**sql_guard rejects CTE queries**~~ — fixed in task 0012 (**done**).
- ~~**LLM budget not reset per turn**~~ — fixed in task 0013 (**done**).
- ~~**Unformatted phone values leak through name-flagged PII columns**~~ — fixed in task 0014 (**done**).
- ~~**Connection-level LLM outages skip the fallback provider**~~ — fixed in task 0015 (**done**).
- ~~**Stale CLI diagnostics after non-analysis turns; docs test-count drift; brittle live eval token**~~ — fixed in task 0016 (**done**).
- ~~**PII markers over-match**~~ — fixed in task 0017 (**done**).
- ~~**/save persists non-analysis output**~~ — fixed in task 0018 (**done**).
- ~~**Malformed trio file crashes CLI startup**~~ — fixed in task 0019 (**done**).
- ~~**Preference regex hijacks analysis questions**~~ — fixed in task 0020 (**done**).
- ~~**Tooling polish**~~ — fixed in task 0021 (**done**).
- Candidate JSONL grows without automatic pruning — curation workflow documented only.
- ~~Explicit oversized SQL `LIMIT` values are not clamped yet; MCP query payloads are not independently row-capped~~ — fixed in task 0022 (**done**).
- ~~LLM guard label parser uses substring matching and can misread negated/mixed labels~~ — fixed in task 0023 (**done**).
- ~~Valid empty query results currently take the same retry path as failures~~ — fixed in task 0024 (**done**).
- ~~Dry-run eval is strong for orchestration but not live NL-to-SQL quality; no CI gate exists yet~~ — fixed in task 0025 (**done**): `.github/workflows/ci.yml`.
- ~~Human docs need final assignment/dataset alignment to remove overclaims and clarify schema/eval/setup details~~ — fixed in task 0026 (**done**): `docs/SCHEMA.md` + README/docs drift fixes.
- ~~**Embedding retrieval returns arbitrary top-k for unrelated questions**~~ — fixed in task 0028 (**done**): cosine similarity floor; version **0.24.0**.
- ~~**Malformed LLM guard classifier output defaults to analysis**~~ — fixed in task 0030 (**done**): fail-closed to `off_topic`; version **0.26.0**.
- ~~**Ambiguous input fails open when guard classifier unavailable**~~ — fixed in task 0033 (**done**): budget/quota classify-skip fails closed; version **0.28.0**.
- ~~**Keyword fallback injects weak one-token overlaps**~~ — fixed in task 0034 (**done**): minimum shared-token floor; version **0.29.0**.
- **Golden Bucket hardening** (task 0027, **pending_review**): zero-overlap keyword fallback, `report_complete` capture gating; version **0.23.0**.
- Preference phrase detection is deterministic and may miss unusual phrasing.
- Live eval gate requires LLM + BigQuery credentials; dry-run is CI-default.
- llama3.2 (local) SQL quality: complex questions (e.g. cancelled-order share) can exhaust 3 self-heal attempts; Gemini fallback or a larger local model handles them.

## Version

- Project version **0.29.0** in `pyproject.toml` and `src/retail_agent/__init__.py` (task 0034 golden keyword fallback relevance floor).
