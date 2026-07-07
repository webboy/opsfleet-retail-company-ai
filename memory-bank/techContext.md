# Tech Context

## Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Language | Python 3.11+ | |
| Agent framework | LangGraph (LangChain v1 ecosystem) | assignment preference |
| LLM | Google Gemini via `langchain-google-genai` (default `gemini-2.5-flash`, env-configurable) | free AI Studio key; mind rate limits |
| LLM fallback | OpenRouter / Ollama (optional) | Opsfleet client: https://github.com/Opsfleet/lc-openrouter-ollama-client |
| Data warehouse | Google BigQuery, public dataset `bigquery-public-data.thelook_ecommerce` | tables: `orders`, `order_items`, `products`, `users`; 1 TB/month free compute |
| DataFrames | pandas + `db-dtypes` | |
| Local persistence | SQLite (saved reports, user prefs) + JSONL (interaction log) | zero-ops, fits prototype |
| Golden Bucket (prototype) | local files + embeddings retrieval, keyword fallback | production: GCS + Vertex AI Vector Search |
| Testing | pytest | mocked LLM/BQ for graph tests |
| Config | `.env` via `python-dotenv` (+ `.env.example`) | |

## Dependencies (baseline from assignment)

```
langgraph>=0.2.0
langchain-google-genai>=1.0.0
google-cloud-bigquery>=3.13.0
pandas>=2.0.0
python-dotenv>=1.0.0
langchain_core>=0.3.0
db-dtypes==1.2.0
```

Add as needed: `pytest`, `rich` (CLI rendering), `pyyaml` (personas), packaging via `pyproject.toml` (project version lives there — see `memory-task-minor-version-bump.mdc`).

## External setup requirements

1. **Google Cloud / BigQuery**: user must have a GCP project and be authenticated (`gcloud auth application-default login`), per the BigQuery client libraries docs. Public dataset requires no special grants; queries bill to the user's project (free tier is ample).
2. **Gemini API key**: free from Google AI Studio → `GOOGLE_API_KEY` in `.env`.
3. Runnable on another machine: plain `pip install -r requirements.txt` (or `pip install -e .`) + `.env` + auth. Docker optional, not required.

## Environment variables (planned)

| Var | Purpose |
|-----|---------|
| `GOOGLE_API_KEY` | Gemini |
| `GCP_PROJECT_ID` | BigQuery billing project |
| `RETAIL_AGENT_MODEL` | model override |
| `RETAIL_AGENT_PERSONA` | persona file selector |
| `LANGSMITH_API_KEY` / `LANGSMITH_TRACING` | optional tracing |
| `OPENROUTER_API_KEY` / `OLLAMA_HOST` | optional LLM fallback |

## Technical constraints

- Gemini free-tier rate limits → retry with backoff, cap LLM calls per turn, keep prompts lean.
- BigQuery costs → `maximum_bytes_billed` on every job, `LIMIT` injection, only 4 allowed tables.
- The dataset is regenerated/rolling — assertions in evals must be property-based (column names, non-empty, ordering), not exact values.
- CLI-only UI. No secrets in the repo or in memory-bank/task files.

## Reference material

- Assignment PDF: `docs/AI Technical Assignment - Retail Company.pdf` (includes `bq_client.py` skeleton and `requirements.txt`).
- LangChain/LangGraph quickstarts: https://docs.langchain.com/oss/python/langchain/quickstart , https://docs.langchain.com/oss/python/langgraph/quickstart , https://docs.langchain.com/oss/python/langgraph/add-memory
