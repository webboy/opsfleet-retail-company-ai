# Retail Agent

A retail data-analysis chat assistant for non-technical executives. A Store Manager asks *"How did monthly revenue trend last year?"* five minutes before a call — and gets an analyst-style answer backed by live SQL, not a data dump.

This repository is the **Opsfleet AI Technical Assignment** prototype: LangGraph agent, BigQuery (`thelook_ecommerce`), Golden Bucket retrieval, safety guards, saved reports, observability, and a QA eval suite.

## Documentation map

| Document | What it covers |
|----------|----------------|
| [Architecture](docs/ARCHITECTURE.md) | Production HLD, Mermaid diagrams, prototype vs production |
| [Technical Explanation](docs/TECHNICAL_EXPLANATION.md) | Technology choices, data flow, error handling, requirements |
| [Schema & Supported Questions](docs/SCHEMA.md) | Allowed tables, joins, dataset boundaries, supported-question matrix |
| [Usage Guide](docs/USAGE.md) | CLI commands, personas, golden trios, traces, artifacts |
| [Evaluation Guide](docs/EVALUATION.md) | pytest, eval suite, judge scoring, baseline workflow |
| [MCP Server](docs/MCP.md) | Optional guarded BigQuery + Golden Bucket MCP tools |

Assignment brief: `docs/AI Technical Assignment - Retail Company.pdf`

## Quick setup

**Prerequisites:** Python 3.11+, a [Google Cloud](https://cloud.google.com/) project, [Gemini API key](https://aistudio.google.com/) (free tier), and the `gcloud` CLI.

```bash
git clone https://github.com/webboy/opsfleet-retail-company-ai.git
cd opsfleet-retail-company-ai

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"            # runtime + pytest (canonical install)

cp .env.example .env
# Edit .env — at minimum:
#   GOOGLE_API_KEY=...
#   GCP_PROJECT_ID=your-gcp-billing-project   # BigQuery job billing, not dataset storage

gcloud auth application-default login   # ADC required for live BigQuery queries
```

Run from the **repository root** so relative paths (`personas/`, `golden_bucket/`, `evals/`) resolve correctly.

> **Note:** `requirements.txt` is a legacy assignment artifact. Use `pip install -e ".[dev]"` — it matches `pyproject.toml` (includes OpenRouter/Ollama deps and pytest).

### Start chatting

```bash
retail-agent --user alice
# equivalent: python -m retail_agent.cli --user alice
```

Optional flags: `--thread <id>` (conversation memory), `--log-level DEBUG|INFO|WARNING|ERROR`.

## Example session — one manager workflow

Curated transcript showing a continuous Store Manager session (analysis → follow-up → preference → save → guarded delete). Format matches the shipped CLI; report wording and dates vary with live data. Bracketed lines such as `[sql attempts=1]` are real CLI diagnostics printed **after** analysis answers only.

```
Retail Agent CLI — user=alice thread=alice-a1b2c3d4
Persona: default
Type /help for commands.

You: How did monthly revenue trend last year?

Agent: Monthly revenue was strongest in Q4, with December leading the year.
       Completed-order revenue grouped by month shows a steady climb from
       spring through year-end.

[sql attempts=1]
[retrieved trios=['monthly-revenue'] method=embedding]

You: And how does that compare to our top product categories?

Agent: Apparel drives the largest share of category revenue, followed by
       accessories. The category mix stayed consistent with the monthly
       trend — growth was broad-based, not one category alone.

[sql attempts=1]
[retrieved trios=['product-category-revenue'] method=embedding]

You: I prefer tables from now on

Agent: Got it — I'll use table format for your reports from now on.

You: /save

Agent: Saved report "How did monthly revenue trend last year?" to your library.

You: show my reports

Agent: Your saved reports:
       - How did monthly revenue trend last year? (2026-07-08)

You: delete reports mentioning revenue

Agent: I found the following saved reports that match your delete request:
       - How did monthly revenue trend last year? (2026-07-08)

       Reply yes or confirm to delete them, or anything else to cancel.

You: no

Agent: Deletion cancelled. Your reports were not changed.
```

### Guarded delete variants (assignment)

The agent supports mention-based, today-based, and all-reports selectors. Each lists exact matches and requires explicit confirmation (`yes`, `y`, `confirm`, or `delete`).

**Delete by mention** (shown in the workflow above): `delete reports mentioning revenue`

**Delete reports saved today:**

```
You: delete reports we made today

Agent: I found the following saved reports that match your delete request:
       - How did monthly revenue trend last year? (2026-07-08)
       - Product category comparison (2026-07-08)

       Reply yes or confirm to delete them, or anything else to cancel.

You: yes

Agent: Deleted 2 saved report(s).
```

**Delete all my reports:** `delete all my reports` — same confirmation flow, scoped to your user ID only.

### Safety snippets (same CLI)

**PII masking** — emails never appear even if SQL retrieves them:

```
You: Give me customer emails for our top buyers

Agent: Top buyers by spend (contact details masked per policy):
       | rank | total_spend |
       | 1    | $2,450      |
       ...
       Note: Customer contact details were masked per company policy.
```

PII masking is silent in the CLI (no diagnostic line); enable `DEBUG` logging to see mask hits in server logs.

**Unsupported dimension** — the public dataset has no branch/store/region columns; the agent explains and suggests supported dimensions:

```
You: Show revenue by region

Agent: There is no region column in thelook_ecommerce. Try revenue by
       department, traffic source, or product category instead.

[sql attempts=3]
```

## Verify installation (no live API keys needed)

Same checks as CI (see [Evaluation Guide](docs/EVALUATION.md#ci-gate-deterministic-no-api-keys)):

```bash
pip install -e ".[dev]"
pytest -q                          # unit + graph integration tests
python -m retail_agent.evals       # dry-run eval suite (17 cases, baseline compare)
```

With credentials configured, optional manual checks:

```bash
python -m retail_agent.bq                              # BigQuery smoke test
python -m retail_agent.evals --live --no-compare       # live smoke (not in CI)
retail-agent --user alice                              # interactive chat
python -m retail_agent.metrics                         # aggregate observability (after chat)
```

See [Evaluation Guide](docs/EVALUATION.md) for eval flags and baseline workflow.

## Project layout

```
src/retail_agent/     Agent core (graph, nodes, CLI, BQ, LLM, observability, evals)
golden_bucket/        Seed trios (question → SQL → report) + candidate capture
personas/             Hot-reload report tone files (default, formal, punchy)
evals/                QA cases, judge prompt, baseline, run outputs (gitignored)
docs/                 Architecture, technical explanation, usage, evaluation
tests/                pytest suite (mocked LLM/BQ — no live API calls)
logs/                 agent_events.jsonl (gitignored, created at runtime)
data/                 SQLite reports/preferences DB (created at runtime)
```

## Requirements coverage

| # | Requirement | Code | Documentation |
|---|-------------|------|---------------|
| 1 | Hybrid Intelligence (Golden Bucket) | `src/retail_agent/golden.py`, `nodes/retrieve_trios.py`, `nodes/capture_candidate.py` | [Architecture — Golden Bucket](docs/ARCHITECTURE.md#golden-bucket-lifecycle), [Technical §1](docs/TECHNICAL_EXPLANATION.md#1-hybrid-intelligence-golden-bucket) |
| 2 | Safety & PII Masking | `src/retail_agent/safety.py`, `nodes/input_guard.py`, `nodes/pii_mask.py`, `nodes/output_mask.py` | [Technical §2](docs/TECHNICAL_EXPLANATION.md#2-safety-and-pii-masking), [Usage — safety](docs/USAGE.md#safety-behavior) |
| 3 | High-Stakes Oversight (saved reports) | `src/retail_agent/stores.py`, `nodes/reports_router.py` | [Technical §3](docs/TECHNICAL_EXPLANATION.md#3-high-stakes-oversight-saved-reports), [Usage — reports](docs/USAGE.md#saved-reports) |
| 4 | Continuous Improvement | `src/retail_agent/stores.py`, `nodes/preferences_router.py`, `golden.py` (candidates) | [Technical §4](docs/TECHNICAL_EXPLANATION.md#4-continuous-improvement-learning-loop), [Usage — preferences](docs/USAGE.md#preferences) |
| 5 | Resilience & Error Handling | `src/retail_agent/graph.py`, `nodes/execute_bq.py`, `nodes/generate_sql.py`, `src/retail_agent/llm.py` | [Technical §5](docs/TECHNICAL_EXPLANATION.md#5-resilience-and-graceful-error-handling), [Architecture — turn flow](docs/ARCHITECTURE.md#agent-turn-flow) |
| 6 | Quality Assurance | `src/retail_agent/evals/`, `evals/cases.yaml` | [Evaluation Guide](docs/EVALUATION.md) |
| 7 | Observability | `src/retail_agent/observability.py`, `trace.py`, `metrics.py` | [Technical §7](docs/TECHNICAL_EXPLANATION.md#7-observability), [Usage — observability](docs/USAGE.md#observability) |
| 8 | Agility (Personas) | `src/retail_agent/personas.py`, `personas/` | [Technical §8](docs/TECHNICAL_EXPLANATION.md#8-agility-persona-management), [Usage — personas](docs/USAGE.md#personas) |

## License

MIT — see [LICENSE](LICENSE).
