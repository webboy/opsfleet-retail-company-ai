# Usage Guide

How to run the retail analysis agent CLI, manage personas and golden trios, inspect observability output, and understand runtime artifacts.

See also: [README](../README.md) (quick setup), [Schema & Supported Questions](./SCHEMA.md), [Architecture](./ARCHITECTURE.md), [Technical Explanation](./TECHNICAL_EXPLANATION.md), [Evaluation Guide](./EVALUATION.md), [MCP Server](./MCP.md).

## CLI entry points

| Command | Purpose |
|---------|---------|
| `retail-agent --user <id>` | Interactive chat (installed console script) |
| `python -m retail_agent.cli --user <id>` | Same as above |
| `python -m retail_agent.bq` | BigQuery smoke test (optional SQL argument) |
| `python -m retail_agent.metrics` | Aggregate metrics from `logs/agent_events.jsonl` |
| `python -m retail_agent.trace <turn_id>` | Reconstruct one turn from the event log |
| `python -m retail_agent.evals` | QA eval suite (dry-run by default) |
| `retail-agent-mcp` | Optional MCP server (stdio; guarded query + trio retrieval) |

Run all commands from the **repository root** so relative paths resolve.

## Chat CLI flags

```bash
retail-agent --user alice
retail-agent --user alice --thread my-session-1
retail-agent --user alice --log-level DEBUG
```

| Flag | Required | Description |
|------|----------|-------------|
| `--user` | Yes | User identity for saved reports, preferences, and observability events |
| `--thread` | No | Conversation thread ID for LangGraph memory (default: `{user}-{random}`) |
| `--log-level` | No | `DEBUG`, `INFO`, `WARNING`, or `ERROR` (default: `INFO`) |

## In-session commands

Type these at the `You:` prompt:

| Command / phrase | Action |
|------------------|--------|
| `/help` | Show built-in help |
| `/save` | Save the most recent report to your library |
| `/prefs` | Show saved output format preferences |
| `/persona <name>` | Switch report tone for this session (`default`, `formal`, `punchy`) |
| `/exit`, `/quit` | End the session |
| `show my reports` | List saved reports |
| `save this report` | Same as `/save` |
| `delete reports mentioning <term>` | Start guarded delete flow (confirmation required) |
| `I prefer tables from now on` | Save table-format preference |
| `give me bullet points from now on` | Save bullet-format preference |
| `What tables do you have?` | Schema question — answered from static docs, no BigQuery |

See [Schema & Supported Questions](./SCHEMA.md) for the supported-question matrix and dataset boundaries.

### Delete confirmation flow

When you request a delete, the agent lists **exact** candidate reports scoped to your user ID, then pauses. Reply `yes`, `y`, `confirm`, or `delete` to proceed; anything else cancels. Cross-user deletion is not possible.

### CLI output hints

After each answer the CLI may print diagnostic lines (not part of the report):

```
[sql attempts=1]
[retrieved trios=['monthly-revenue'] method=embedding]
```

- **sql attempts** — how many SQL generation/execution cycles ran (up to 3 on SQL or guard errors).
- **retrieved trios** — golden bucket examples injected into the SQL prompt.

## Personas

Personas control report **tone and style**. They live in `personas/` as plain Markdown or YAML files.

| File | Tone |
|------|------|
| `personas/default.md` | Balanced analyst voice |
| `personas/formal.md` | Executive briefing style |
| `personas/punchy.md` | Short, direct headlines |

**Default persona:** set `RETAIL_AGENT_PERSONA=default` in `.env`.

**Runtime override:** `/persona formal` switches tone for the current CLI session only.

**Hot reload:** persona files are re-read on every `compose_report` turn — edit a file and the next answer picks up the change without restarting the CLI.

**Custom directory:** set `RETAIL_AGENT_PERSONAS_DIR` in `.env`.

## Golden Bucket trios

Expert **trios** (question → SQL → report excerpt) ground SQL generation and report style.

### Layout

```
golden_bucket/
  monthly-revenue.md      # seed trio (YAML front-matter + report body)
  product-category-revenue.md
  ...
  candidates/
    candidates.jsonl      # captured successful turns awaiting review
```

Each seed file uses YAML front-matter:

```yaml
---
id: monthly-revenue
question: How did monthly revenue trend last year?
sql: |
  SELECT ...
tags: [revenue, time-series]
---
Analyst report excerpt shown to the LLM as style guidance.
```

### Adding a trio

1. Create `golden_bucket/<id>.md` with front-matter (`id`, `question`, `sql`, optional `tags`) and a short report excerpt.
2. Restart the CLI (embeddings load at `TrioStore` initialization).
3. Ask a similar question — the trio should appear in `[retrieved trios=...]`.

Malformed trio files (missing required keys, invalid YAML, or missing front matter) are **skipped** with a warning in the logs; the agent keeps running with the remaining valid trios. Fix or remove bad files during curation.

### Candidate capture

After a successful **SQL analysis turn** with a fully composed report (`status=done`, `report_complete=True`, question, SQL, and report), the graph **automatically** appends a candidate to `golden_bucket/candidates/candidates.jsonl`. This is not user-controlled — budget-exhausted compose messages, fallback turns, schema answers, refusals, and chitchat are not captured. Promote approved candidates into new seed files manually (prototype has no analyst UI).

### Custom bucket path

Set `GOLDEN_BUCKET_DIR` in `.env` to point at an alternate directory.

## Saved reports

Reports are stored in SQLite (default: `./data/reports.sqlite3`). Override with `RETAIL_AGENT_DB_PATH`.

Each report record includes owner, title, content, originating question, SQL, timestamps, and tags. Only the owning user can list or delete their reports.

## Preferences

Per-user output format (`table`, `bullets`, `prose`) is stored in the same SQLite database and injected into every `compose_report` call. Preferences survive CLI restarts.

## Provider fallback

Configure in `.env`:

```bash
RETAIL_AGENT_PROVIDER=gemini
RETAIL_AGENT_FALLBACK_PROVIDER=openrouter   # optional
OPENROUTER_API_KEY=...
```

Supported providers: `gemini` (default), `openrouter`, `ollama`. On primary quota/outage after retries, the agent transparently tries the fallback within the per-turn LLM call budget (default 8 calls).

## Safety behavior

| Concern | Mechanism |
|---------|-----------|
| Prompt injection / off-topic | `input_guard` refuses early — no BigQuery |
| Destructive SQL language | `input_guard` refuses |
| Non-SELECT / wrong tables | `sql_guard` inside `BigQueryRunner` blocks before job submission |
| PII in results | `pii_mask` on DataFrame + `output_mask` regex on final text |
| Report deletes | Owner-scoped list + LangGraph `interrupt()` confirmation |

`sql_guard` is **not** a separate graph node. It runs inside `execute_bq` via `BigQueryRunner.execute()`. Guard violations trigger the self-heal retry loop (up to 3 attempts) and then `fallback_answer`.

## Observability

Every graph node emits structured JSONL events to `logs/agent_events.jsonl` (gitignored). Events include turn ID, user, node name, latency, SQL text, error class, retry count, guard decisions, trio IDs, and PII mask hits. Full prompts and result rows are **not** logged.

### Metrics

```bash
python -m retail_agent.metrics
python -m retail_agent.metrics --json
python -m retail_agent.metrics --log-path logs/agent_events.jsonl
```

Sample output:

```
Agent metrics summary
  turns: 12
  success_rate: 83.3%
  fallback_rate: 8.3%
  guard_block_rate: 0.0%
  self_heal_events: 2
  pii_mask_hits: 1
  latency_ms: p50=4200 p95=8900
```

### Trace replay

Turn IDs are written to `logs/agent_events.jsonl`, not printed in the CLI banner. After a chat session:

```bash
# Find a turn_id in logs/agent_events.jsonl, then:
python -m retail_agent.trace <turn_id>
```

### LangSmith (optional)

Set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` for full LLM trace export alongside JSONL events.

## MCP server (optional)

Install and run the guarded MCP server for external clients (Cursor, Claude Desktop):

```bash
pip install -e ".[mcp]"
retail-agent-mcp
```

See [MCP Server Guide](./MCP.md) for tool schemas, client registration, and safety boundaries.

## Runtime artifacts

| Path | Created by | Gitignored |
|------|------------|------------|
| `logs/agent_events.jsonl` | `TurnTracer` during chat | Yes |
| `data/reports.sqlite3` | `ReportStore` on first save/prefs | Yes (directory) |
| `golden_bucket/candidates/candidates.jsonl` | `capture_candidate` node | No (local learning seam) |
| `evals/runs/*.jsonl` | Eval runner (optional `--output`) | Yes |

## Environment variables

Copy `.env.example` → `.env`. Minimum for live chat:

- `GOOGLE_API_KEY` — Gemini (AI Studio)
- `GCP_PROJECT_ID` — **your** Google Cloud project used for BigQuery **job billing** when querying the public `thelook_ecommerce` dataset (storage stays in `bigquery-public-data`)
- `gcloud auth application-default login` — Application Default Credentials (ADC) for the BigQuery client

See `.env.example` for optional overrides: model IDs, embedding model, persona, dataset, bytes billed, provider fallback, DB path, personas dir, golden bucket dir, LangSmith.
