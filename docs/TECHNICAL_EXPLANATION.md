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

**Guardrails (always on):** Deterministic `sql_guard` before execution — SELECT-only, single statement, four allowed tables, LIMIT injection, bytes billed cap. Defense in depth even when the dataset is public/read-only.

### Golden Bucket storage and retrieval

**Production:** Trios stored as objects in **Google Cloud Storage**; question embeddings indexed in **Vertex AI Vector Search** (or equivalent managed vector DB). Analyst curation pipeline promotes approved candidates.

**Prototype:** Trios as YAML/Markdown files under `golden_bucket/` (one file per trio with YAML front-matter: `id`, `question`, `sql`, `tags`, `report`); question embeddings via Gemini (`gemini-embedding-001` by default, overridable with `RETAIL_AGENT_EMBEDDING_MODEL`) with in-memory cosine similarity; **keyword-overlap fallback** when the embedding API is unavailable. Successful turns append to `golden_bucket/candidates/candidates.jsonl`. Override the bucket location with `GOLDEN_BUCKET_DIR` if needed.

**Reasoning:** Vector search scales to thousands of trios with sub-second retrieval. Local files keep the prototype zero-ops while preserving the same retrieval → inject → generate SQL flow.

### Application persistence

| Data | Production | Prototype |
|------|------------|-----------|
| Saved reports | Cloud SQL or Firestore | SQLite (`RETAIL_AGENT_DB_PATH`, default `./data/reports.sqlite3`) |
| User preferences | Cloud SQL or Firestore | SQLite (`preferences` table in `RETAIL_AGENT_DB_PATH`) |
| Personas | GCS objects or CMS | Local `personas/` files, hot-read each turn (`RETAIL_AGENT_PERSONAS_DIR`) |
| Conversation threads | Checkpointer + managed store | LangGraph SQLite/in-memory checkpointer |
| Observability / eval runs | Cloud Logging + GCS JSONL | Local `logs/agent_events.jsonl` |

**Reasoning:** SQLite and local files eliminate infrastructure for the prototype. Production moves to managed services for durability, backup, and multi-instance agent replicas.

### Observability and QA tooling

**Production:** Structured JSON logs → Cloud Logging; metric dashboards and alerts in Cloud Monitoring; optional **LangSmith** for full LLM trace replay.

**Prototype:** Per-node JSONL events; CLI commands to reconstruct a turn (`trace`) and summarize metrics (`metrics`); optional LangSmith when env vars are set.

**Eval gate:** pytest unit tests for pure logic; full eval suite (`evals/`) with property assertions, safety cases, and LLM-as-judge intent scoring — run before deploy; results persisted for regression comparison.

---

## Runtime data flow

A single analysis turn proceeds as follows:

1. **Client** sends natural-language message with user identity and thread ID.
2. **input_guard** classifies intent. Malicious/off-topic → polite refusal (no BigQuery, minimal LLM).
3. **retrieve_trios** embeds the question, searches the Golden Bucket index, returns top-k Trios.
4. **generate_sql** calls the LLM with: table schemas, retrieved trios, conversation history, and safety instructions.
5. **sql_guard** validates generated SQL. Failure → user-facing policy message (no execution).
6. **execute_bq** submits the job. On syntax error, permission error, or empty result → **self_heal** loop (feed error + prior SQL to LLM, retry up to N times).
7. **pii_mask** scrubs email/phone columns in the DataFrame and regex-sweeps the composed report.
8. **compose_report** calls the LLM with masked rows, active persona, and user format preference.
9. **Response** returned to client; optional prompt to save report.
10. **Observability** emits one structured event per node (latency, SQL text, error class, retry count, mask hits).
11. **Learning seam:** successful turn may append a candidate trio for analyst review.

Report-management turns skip steps 3–8 and route through **reports_router** (save/list/delete with confirmation interrupt). Preference turns route through **preferences_router** (save/show output format without LLM).

---

## Error handling and fallback strategies

| Failure | Detection | Response | Cost control |
|---------|-----------|----------|--------------|
| **LLM rate limit (429)** | HTTP status from provider | Exponential backoff; optional fallback provider; if exhausted → graceful "try again shortly" | Per-turn LLM call budget |
| **LLM outage (5xx)** | Provider errors | Retry; fallback provider; graceful apology if all fail | Same budget |
| **Bad SQL syntax** | BigQuery error message | Self-heal: LLM regenerates SQL with error context (max N retries) | Retries bounded; bytes cap on each attempt |
| **Empty result set** | Zero rows returned | Self-heal: LLM revises query (e.g. wrong filter/date); then fallback suggestion | Same |
| **sql_guard violation** | Static linter | No BigQuery call; explain which rule failed | Zero query cost |
| **BigQuery timeout / quota** | Job API error | User-facing retry suggestion; log error class | `maximum_bytes_billed` prevents runaway scans |
| **Embedding API down** | Embed call failure | Keyword overlap retrieval over local trios | Degraded but functional |
| **PII in SQL result** | Column names + content regex | Deterministic mask before LLM sees rows; output regex sweep | N/A |
| **Delete without confirmation** | Graph state | `interrupt()` pauses until explicit yes; anything else cancels | N/A |
| **UI crash** | Uncaught exception at CLI | Top-level handler returns generic apology; never stack trace to user | N/A |

**Principle:** Every failure path produces a complete user-facing sentence. The CLI and future web UI never crash on agent errors.

---

## Setup and run (overview)

Detailed step-by-step setup (venv, GCP auth walkthrough, example transcripts) will ship with the repository README once the prototype is implemented. At a high level:

### Prerequisites

- Python 3.11+
- Google Cloud account with BigQuery access (1 TB/month free compute tier is sufficient)
- Gemini API key from [Google AI Studio](https://aistudio.google.com/) (free tier; mind rate limits)

### Environment

```bash
# Clone the repository, create a virtual environment, install dependencies
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .

# Authenticate for BigQuery (Application Default Credentials)
gcloud auth application-default login

# Configure environment (copy .env.example → .env)
# GOOGLE_API_KEY=...
# GCP_PROJECT_ID=your-billing-project
```

### Example run (once prototype is available)

```bash
python -m retail_agent.cli --user alice
# Ask: "What was our monthly revenue last quarter?"
# Ask: "Who are our top 10 customers by total spend?"
# Follow-up: "And how does that compare to the previous quarter?"
```

Optional: set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` for full trace export. LLM provider env vars: `RETAIL_AGENT_PROVIDER`, `RETAIL_AGENT_FALLBACK_PROVIDER`, `OPENROUTER_API_KEY`, `RETAIL_AGENT_OPENROUTER_MODEL`, `OLLAMA_HOST`, `RETAIL_AGENT_OLLAMA_MODEL`.

---

## Requirement-by-requirement design

### 1. Hybrid Intelligence (Golden Bucket)

**Problem:** SQL alone cannot capture how analysts interpret ambiguous business questions. Expert Trios encode question → SQL → report patterns.

**Query-time retrieval:** Embed the user question → vector search top-k Trios → inject as few-shot examples in the SQL-generation prompt. Keyword fallback if embeddings fail.

**Update over time:** Successful agent turns write **candidate** trios (question, SQL, report) to a review queue — not directly into golden. Analysts approve, edit, or reject. Approved trios are written to GCS, re-embedded, and indexed. Rejected candidates are archived. This prevents low-quality automation from polluting expert knowledge.

**Prototype:** Local seed trios + `golden_bucket/candidates/` capture; curation UI documented only. **Production:** GCS + Vertex AI Vector Search + analyst review workflow.

---

### 2. Safety and PII Masking

**Problem:** Raw logs contain customer emails and phones; the agent must answer analysis questions only and never display PII, even if SQL retrieves it.

**Input guard:** First graph node (`input_guard`) applies deterministic rules for obvious prompt injection, destructive SQL language, and off-topic requests, then uses a small LLM fallback only for ambiguous turns. Refusals exit early with a polite message — no Golden Bucket retrieval or BigQuery.

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

**4b — System level:** Successful turns capture candidate trios (see Requirement 1). Interaction logs feed eval baselines and analyst review. Over time, approved trios improve retrieval quality for all users.

**Prototype:** SQLite preferences in `src/retail_agent/stores.py` + local candidate capture. **Production:** Managed DB + GCS curation pipeline.

---

### 5. Resilience and Graceful Error Handling

**Problem:** SQL errors and empty results must self-correct; the UI must not crash; costs must not inflate; third-party APIs fail.

**Self-heal loop:** On BigQuery error or zero rows, feed error message + previous SQL to the LLM; regenerate; retry up to N (default 2). After exhaustion → graceful fallback ("I couldn't find an answer; try rephrasing…").

**Resilience elsewhere:** LLM retry/backoff; optional provider fallback; embedding keyword fallback; top-level CLI exception handler; per-turn LLM call budget; sql_guard prevents expensive bad queries.

**Prototype and production:** Same graph logic; production adds circuit breakers and alerting on elevated self-heal rates.

---

### 6. Quality Assurance

**Problem:** How to evaluate the agent before deployment and verify reports match user intent.

**Three-layer eval suite:**

| Layer | What it checks | How |
|-------|----------------|-----|
| **Capability cases** | ~15–20 questions across customer behavior, product performance, time metrics, schema questions | Property assertions: expected tables referenced, non-empty results, must/must-not-contain strings (dataset is rolling — no exact value assertions) |
| **Safety cases** | Injection refused, PII masked, delete requires confirmation, off-topic declined | Deterministic pass/fail |
| **Intent correctness** | Does the report answer the question? | LLM-as-judge: inputs = question + SQL + result sample + report → score 1–5 + rationale |

**Gate:** Eval runner produces pass/fail table + aggregate judge score; results persisted (JSONL) for regression comparison against stored baseline. CI blocks deploy on regression.

**Prototype:** Local runner + pytest for assertion engine. **Production:** Same suite in CI/CD; scheduled nightly runs against staging agent.

---

### 7. Observability

**Problem:** Know when and why the agent fails; support deep-dive debugging of message correspondence.

**Structured events (every node):** turn id, user, node name, latency ms, model, SQL text, error class, retry count, guard decision, trios retrieved, PII mask hit count, tokens (when available).

**Metrics tracked:** turn success rate, self-heal rate, SQL failure classes, guard-block rate, PII mask hits, p50/p95 latency, tokens per turn.

**Deep dive:** Reconstruct full turn from turn id (messages, SQL attempts, mask actions, final report). Optional LangSmith trace for LLM-level debugging.

**Prototype:** JSONL log + CLI `trace` / `metrics`. **Production:** Cloud Logging + Monitoring dashboards + alert policies (e.g. success rate drop, spike in guard blocks).

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

- [Architecture](./ARCHITECTURE.md) — production HLD, Mermaid diagrams, extensibility (including MCP), prototype vs production mapping.
