# Technical Explanation — Retail Data Analysis Chat Assistant

This document explains **why** the system is built the way it is, how data flows at runtime, how failures are handled, and how each of the eight assignment requirements is addressed in production (with prototype equivalents where they differ). For component diagrams and the Golden Bucket lifecycle, see [Architecture](./ARCHITECTURE.md).

---

## Technology choices

### Agent framework: LangGraph (LangChain v1 ecosystem)

**Choice:** LangGraph state machine with explicit nodes, conditional edges, checkpointers, and `interrupt()` for human-in-the-loop confirmations.

**Reasoning:** The assignment prefers LangGraph. Retail agent flows are inherently stateful graphs: guard branches, self-heal loops, delete confirmations, and conversation memory map directly to graph primitives. A plain "call tools in a loop" design would re-implement interrupts, retry bounds, and checkpoint persistence by hand.

**Production:** Agent service runs as a container (Cloud Run or GKE) hosting the compiled graph. **Prototype:** Same graph in-process behind a CLI REPL.

### LLM: Google Gemini

**Choice:** Default model class `gemini-2.5-flash` (fast, cost-effective) via `langchain-google-genai`; model ID configurable by environment variable.

**Reasoning:** Assignment recommends newer Gemini models; AI Studio provides a free tier suitable for development. Flash-class models balance latency and cost for SQL generation and report composition. A separate judge model (or same model, different prompt) powers eval intent scoring.

**Production:** Vertex AI Gemini with project-level quotas, billing alerts, and optional model routing. **Prototype:** AI Studio API key (`GOOGLE_API_KEY`).

**Fallback:** Configurable primary provider via `RETAIL_AGENT_PROVIDER` (`gemini`, `openrouter`, `ollama`) with optional `RETAIL_AGENT_FALLBACK_PROVIDER`. On quota exhaustion or primary outage after retries, the agent transparently retries on the fallback provider within the same per-turn LLM budget. OpenRouter uses an OpenAI-compatible endpoint; Ollama uses a local host.

### Data warehouse: Google BigQuery

**Choice:** Read-only SQL access to `bigquery-public-data.thelook_ecommerce` (prototype) / company BigQuery project (production). Tables: `orders`, `order_items`, `products`, `users`.

**Reasoning:** Assignment specifies this dataset. BigQuery handles ad-hoc analyst queries at scale, integrates with GCP IAM, and offers `maximum_bytes_billed` for cost caps. pandas DataFrames via the official client suit the report-composition step.

**Guardrails (always on):** Deterministic `sql_guard` before execution — SELECT-only, single statement, four allowed tables, LIMIT injection/clamping to `BQ_DEFAULT_LIMIT`, bytes billed cap. Defense in depth even when the dataset is public/read-only.

### Golden Bucket storage and retrieval

**Production:** Trios stored as objects in **Google Cloud Storage**; question embeddings indexed in **Vertex AI Vector Search** (or equivalent managed vector DB). Analyst curation pipeline promotes approved candidates.

**Prototype:** Trios as YAML/Markdown files under `golden_bucket/` (one file per trio with YAML front-matter: `id`, `question`, `sql`, `tags`, `report`); question embeddings via Gemini (`gemini-embedding-001` by default, overridable with `RETAIL_AGENT_EMBEDDING_MODEL`) with in-memory cosine similarity; **keyword-overlap fallback** when the embedding API is unavailable — if no trio shares tokens with the question, retrieval returns no examples instead of arbitrary top-k matches. Embedding retrieval is best-effort and separate from the per-turn LLM generation/composition call budget. Complete successful analysis turns append to `golden_bucket/candidates/candidates.jsonl`. Override the bucket location with `GOLDEN_BUCKET_DIR` if needed.

**Reasoning:** Vector search scales to thousands of trios with sub-second retrieval. Local files keep the prototype zero-ops while preserving the same retrieval → inject → generate SQL flow.

### Application persistence

| Data | Production | Prototype |
|------|------------|-----------|
| Saved reports | Cloud SQL or Firestore | SQLite (`RETAIL_AGENT_DB_PATH`, default `./data/reports.sqlite3`) |
| User preferences | Cloud SQL or Firestore | SQLite (`preferences` table in `RETAIL_AGENT_DB_PATH`) |
| Personas | GCS objects or CMS | Local `personas/` files, hot-read each turn (`RETAIL_AGENT_PERSONAS_DIR`) |
| Conversation threads | Checkpointer + managed store | LangGraph `MemorySaver` (in-process, per CLI session) |
| Observability / eval runs | Cloud Logging + GCS JSONL | Local `logs/agent_events.jsonl` |

**Reasoning:** SQLite and local files eliminate infrastructure for the prototype. Production moves to managed services for durability, backup, and multi-instance agent replicas.

### Observability and QA tooling

**Production:** Structured JSON logs → Cloud Logging; metric dashboards and alerts in Cloud Monitoring; optional **LangSmith** for full LLM trace replay.

**Prototype:** Per-node JSONL events written to `logs/agent_events.jsonl` (safe summaries only — no full result rows or prompt dumps). Commands:

```bash
python -m retail_agent.metrics              # aggregate success/fallback/guard/latency metrics
python -m retail_agent.trace <turn_id>      # reconstruct one turn's node sequence
```

Optional LangSmith: set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` for full LLM trace export.

**Eval gate:** `pytest` for pure logic; full eval suite under `evals/` with property assertions, safety cases, and LLM-as-judge intent scoring. Default runner is dry-run (no live API keys); use `--live --no-compare` for optional manual smoke tests against real Gemini + BigQuery:

```bash
python -m retail_agent.evals                          # dry-run default; compares to evals/baseline/dry-run-v0.8.0.jsonl
python -m retail_agent.evals --live --no-compare      # optional live smoke (requires .env + BigQuery auth)
python -m retail_agent.evals --layer safety           # safety subset only
```

---

## Runtime data flow

A single analysis turn proceeds as follows:

1. **Client** sends natural-language message with user identity and thread ID.
2. **input_guard** classifies intent. Malicious/off-topic → polite refusal (no BigQuery, minimal LLM). Schema questions → static schema docs (no BigQuery). Chitchat → short redirect.
3. **retrieve_trios** (analysis only) embeds the question, searches the Golden Bucket index, returns top-k Trios.
4. **generate_sql** calls the LLM with: table schemas, retrieved trios, conversation history, and safety instructions.
5. **execute_bq** runs `sql_guard` (inside `BigQueryRunner`) then submits the job. Guard violations, syntax errors, and permission errors → **self_heal** loop (feed error + prior SQL to LLM, retry up to N times, default **3**). Valid empty result sets are treated as successful queries and go straight to report composition.
6. **pii_mask** scrubs email/phone columns in the DataFrame.
7. **compose_report** calls the LLM with masked rows, active persona, and user format preference.
8. **output_mask** regex-sweeps the final report text for residual PII.
9. **capture_candidate** automatically appends a candidate trio when the turn completes with `status=done`, `report_complete=True`, SQL, and a fully composed report (analysis path only).
10. **Response** returned to client; optional prompt to save report.
11. **Observability** emits one structured event per node (latency, SQL text, error class, retry count, mask hits).

Report-management turns skip steps 3–8 and route through **reports_router** (save/list/delete with confirmation interrupt). Preference turns route through **preferences_router** (save/show output format without LLM).

---

## Error handling and fallback strategies

| Failure | Detection | Response | Cost control |
|---------|-----------|----------|--------------|
| **LLM rate limit (429)** | HTTP status from provider | Exponential backoff; optional fallback provider; if exhausted → graceful "try again shortly" | Per-turn LLM call budget |
| **LLM outage (5xx)** | Provider errors | Retry; fallback provider; graceful apology if all fail | Same budget |
| **Bad SQL syntax** | BigQuery error message | Self-heal: LLM regenerates SQL with error context (max N retries) | Retries bounded; bytes cap on each attempt |
| **Empty result set** | Zero rows returned | Report composition with an empty sample; the LLM explains that no rows matched | Same |
| **sql_guard violation** | Static linter in `BigQueryRunner` | No BigQuery job; error fed into self-heal retry loop (up to 3 attempts), then graceful fallback | Zero query cost per blocked attempt |
| **BigQuery timeout / quota** | Job API error | User-facing retry suggestion; log error class | `maximum_bytes_billed` prevents runaway scans |
| **Embedding API down** | Embed call failure | Keyword overlap retrieval over local trios | Degraded but functional |
| **PII in SQL result** | Column names + content regex | Deterministic mask before LLM sees rows; output regex sweep | N/A |
| **Delete without confirmation** | Graph state | `interrupt()` pauses until explicit yes; anything else cancels | N/A |
| **UI crash** | Uncaught exception at CLI | Top-level handler returns generic apology; never stack trace to user | N/A |

**Principle:** Every failure path produces a complete user-facing sentence. The CLI and future web UI never crash on agent errors.

---

## Setup and run (overview)

Full step-by-step setup, example manager workflow transcript, and verification commands are in the [README](../README.md). This section summarizes the essentials.

### Prerequisites

- Python 3.11+
- Google Cloud account with BigQuery access (1 TB/month free compute tier is sufficient)
- Gemini API key from [Google AI Studio](https://aistudio.google.com/) (free tier; mind rate limits)

### Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"     # runtime + pytest (canonical install from pyproject.toml)

gcloud auth application-default login

cp .env.example .env
# GOOGLE_API_KEY=...
# GCP_PROJECT_ID=your-gcp-billing-project   # BigQuery job billing project (ADC also required)
```

> `requirements.txt` is a legacy assignment artifact. Prefer `pip install -e ".[dev]"` — it includes OpenRouter/Ollama dependencies and pytest.

### Example run

```bash
retail-agent --user alice
# Ask: "How did monthly revenue trend last year?"
# Follow-up: "And how does that compare to our top product categories?"
# Preference: "I prefer tables from now on"
# /save — then "show my reports"
```

Optional: `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` for full trace export. LLM provider env vars: `RETAIL_AGENT_PROVIDER`, `RETAIL_AGENT_FALLBACK_PROVIDER`, `OPENROUTER_API_KEY`, `RETAIL_AGENT_OPENROUTER_MODEL`, `OLLAMA_HOST`, `RETAIL_AGENT_OLLAMA_MODEL`.

See [Usage Guide](./USAGE.md) for all CLI flags and commands.

---

## Requirement-by-requirement design

### 1. Hybrid Intelligence (Golden Bucket)

**Problem:** SQL alone cannot capture how analysts interpret ambiguous business questions. Expert Trios encode question → SQL → report patterns.

**Query-time retrieval:** Embed the user question → vector search top-k Trios → inject as few-shot examples in the SQL-generation prompt. Keyword fallback if embeddings fail.

**Update over time:** Successful SQL analysis turns with fully composed reports automatically write **candidate** trios (question, SQL, report) to a review queue — not directly into golden. Analysts approve, edit, or reject. Approved trios are written to GCS, re-embedded, and indexed. Rejected candidates are archived. Budget-exhausted compose messages, fallback turns, schema answers, chitchat, and refused turns are not captured.

**Prototype:** Local seed trios + `golden_bucket/candidates/` capture; curation UI documented only. **Production:** GCS + Vertex AI Vector Search + analyst review workflow.

---

### 2. Safety and PII Masking

**Problem:** Raw logs contain customer emails and phones; the agent must answer analysis questions only and never display PII, even if SQL retrieves it.

**Input guard:** First graph node (`input_guard`) applies deterministic rules for obvious prompt injection, destructive SQL language, and off-topic requests, then uses a small LLM fallback only for ambiguous turns. The LLM classifier must return one canonical label (`analysis`, `schema`, `chitchat`, `off_topic`, `malicious`) on the first line or as minimal JSON; negated/mixed prose falls back to `analysis` rather than substring matching. Refusals exit early with a polite message — no Golden Bucket retrieval or BigQuery. **Schema questions** route to `answer_schema`, which answers from bundled static documentation only (see [Schema & Supported Questions](./SCHEMA.md)).

**PII masking (deterministic, two layers):**
1. **DataFrame layer (`pii_mask`):** Detect email/phone columns by name (`email`, `phone`, …) and by content sampling; mask values (`j***@***.***`, `***-***-1234`) **before** rows reach the report LLM.
2. **Output layer (`output_mask`):** Regex sweep on final report text for email/phone shapes; append a short PII policy note when masking occurred.

Explicit PII requests (e.g. top buyers with emails) may still run as analysis, but masked output is mandatory.

**Prototype:** Full implementation as first-class feature. **Production:** Same logic; optional DLP API scan as additional layer.

---

### 3. High-Stakes Oversight (Saved Reports)

**Problem:** The agent manages a Saved Reports library. Deletes ("Delete all reports mentioning Client X", "Delete all reports we made today") are destructive and need strict confirmation without breaking conversational UX.

**Design:**
- Reports stored in SQLite via `ReportStore` (`src/retail_agent/stores.py`) with columns `owner`, title, content, question, sql, timestamps, and tags.
- Default database path: `./data/reports.sqlite3`; override with `RETAIL_AGENT_DB_PATH`.
- Delete request → resolve candidate set **scoped to `owner = current_user`** (mention text, “today”, or “all my reports”) → present exact list (titles + dates) → **LangGraph `interrupt()`** → only explicit confirmation (`yes`, `y`, `confirm`, or `delete`) executes deletion; anything else cancels.
- Empty candidate set → clear message, no interrupt.
- Save and list are conversational (`save this report`, `show my reports`) or slash commands (`/save`); delete confirmation resumes the graph with the user’s next message via `Command(resume=...)`.

**Prototype:** SQLite + CLI. **Production:** Cloud SQL/Firestore + web client; same graph interrupt semantics.

---

### 4. Continuous Improvement (Learning Loop)

**4a — User level:** Per-manager format preferences (`table`, `bullets`, `prose`) are detected deterministically from phrases like "I prefer tables" or `/prefs`, persisted in the shared SQLite store (`preferences` table, keyed by `user_id`), and injected into every `compose_report` system prompt. Survives CLI restart; scoped per user.

**4b — System level:** Successful SQL analysis turns with complete reports automatically capture candidate trios (see Requirement 1). Interaction logs feed eval baselines and analyst review. Over time, approved trios improve retrieval quality for all users.

**Prototype:** SQLite preferences in `src/retail_agent/stores.py` + local candidate capture. **Production:** Managed DB + GCS curation pipeline.

---

### 5. Resilience and Graceful Error Handling

**Problem:** SQL errors and empty results must self-correct; the UI must not crash; costs must not inflate; third-party APIs fail.

**Self-heal loop:** On BigQuery error or sql_guard block, feed error message + previous SQL to the LLM; regenerate; retry up to N (default **3**). After exhaustion → `fallback_answer` with a graceful rephrase suggestion. **Valid empty result sets** (zero rows) are treated as successful queries and go straight to report composition — they do not trigger self-heal.

**Resilience elsewhere:** LLM retry/backoff; optional provider fallback; embedding keyword fallback; top-level CLI exception handler; per-turn LLM call budget; sql_guard prevents expensive bad queries.

**Prototype and production:** Same graph logic; production adds circuit breakers and alerting on elevated self-heal rates.

---

### 6. Quality Assurance

**Problem:** How to evaluate the agent before deployment and verify reports match user intent.

**Three-layer eval suite:**

| Layer | What it checks | How |
|-------|----------------|-----|
| **Capability cases** | **11** questions across customer behavior, product performance, time metrics, and schema questions (see [Schema & Supported Questions](./SCHEMA.md)) | Property assertions: expected tables referenced, non-empty results where applicable, must/must-not-contain strings (dataset is rolling — no exact value assertions) |
| **Safety cases** | **5** cases: injection refused, PII masked, delete requires confirmation, off-topic declined, destructive SQL blocked | Deterministic pass/fail |
| **Intent correctness** | Does the report answer the question? | LLM-as-judge: inputs = question + SQL + result sample + report → score 1–5 + rationale; **score &lt; 3 fails** a passing capability case |

**Gate:** Eval runner produces pass/fail table + aggregate judge score; results persisted (JSONL) for regression comparison against stored baseline. GitHub Actions CI runs `pytest -q` and dry-run eval on every push/PR; a failing regression blocks merge until fixed or the baseline is intentionally updated.

**Prototype:** Local runner + pytest for assertion engine. **Production:** Same suite in CI/CD; scheduled nightly runs against staging agent.

---

### 7. Observability

**Problem:** Know when and why the agent fails; support deep-dive debugging of message correspondence.

**Structured events (every node):** turn id, user, node name, latency ms, model, SQL text, error class, retry count, guard decision, trios retrieved, PII mask hit count.

**Metrics tracked:** turn success rate, fallback rate, self-heal event count, guard-block rate, PII mask hits, p50/p95 latency (via `python -m retail_agent.metrics`).

**Deep dive:** Reconstruct full turn from turn id (messages, SQL attempts, mask actions, final report). Optional LangSmith trace for LLM-level debugging.

**Prototype:** JSONL log at `logs/agent_events.jsonl` + `python -m retail_agent.trace <turn_id>` / `python -m retail_agent.metrics`. **Production:** Cloud Logging + Monitoring dashboards + alert policies (e.g. success rate drop, spike in guard blocks).

---

### 8. Agility (Persona Management)

**Problem:** CEO changes report tone weekly; non-developers must update instructions without redeployment.

**Design:** Persona = plain text or YAML file containing tone/style/system instructions. Default selection via `RETAIL_AGENT_PERSONA`; runtime override via CLI `/persona <name>` for the current session/thread. File content is **re-read on every `compose_report` turn** — editing the file changes the next answer immediately, no restart.

**Production:** Persona objects in GCS or a lightweight CMS/admin page; agent hot-reads each turn. **Prototype:** `personas/default.md`, `personas/formal.md`, `personas/punchy.md` loaded by `src/retail_agent/personas.py`.

User format preferences (Requirement 4a) complement personas: persona = company tone; preferences = individual manager format.

---

## Summary table

| # | Requirement | Primary mechanisms |
|---|-------------|-------------------|
| 1 | Hybrid Intelligence | Vector retrieval + trio injection; curation pipeline |
| 2 | Safety & PII | input_guard + sql_guard + deterministic pii_mask |
| 3 | High-Stakes Oversight | Owner-scoped reports + LangGraph interrupt confirmation |
| 4 | Continuous Improvement | User prefs store + candidate trio capture + curation |
| 5 | Resilience | Self-heal loop + LLM retry/fallback + bounded budgets |
| 6 | Quality Assurance | Eval suite: properties + safety + LLM judge |
| 7 | Observability | Structured JSON events + metrics + trace replay |
| 8 | Agility | Hot-read persona files / GCS objects |

---

## Related documentation

- [Schema & Supported Questions](./SCHEMA.md) — allowed tables, supported-question matrix, schema route.
- [Architecture](./ARCHITECTURE.md) — production HLD, Mermaid diagrams, extensibility (including MCP), prototype vs production mapping.
- [Usage Guide](./USAGE.md) — CLI reference, personas, golden trios, observability.
- [Evaluation Guide](./EVALUATION.md) — pytest, eval suite layers, judge scoring, baseline workflow.
- [MCP Server Guide](./MCP.md) — optional guarded query and trio retrieval server.
