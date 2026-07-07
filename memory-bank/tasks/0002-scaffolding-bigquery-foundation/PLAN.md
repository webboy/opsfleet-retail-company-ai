# Plan — Task 0002

1. Create `pyproject.toml`, `requirements.txt`, `.gitignore`, `.env.example`, `src/retail_agent/` skeleton with `__init__.py` (`__version__ = "0.1.0"`).
2. Implement `config.py` (dotenv + settings: project id, model, persona, limits).
3. Implement `bq.py`: `sql_guard` using **sqlglot** BigQuery dialect (pure function → easy tests), then `BigQueryRunner` with `maximum_bytes_billed`, typed `QueryResult` (ok/error/empty + DataFrame).
4. Tests: pytest for `sql_guard` matrix (select ok, DML blocked, DDL blocked, multi-statement blocked, wrong table blocked, LIMIT injected) + mocked runner tests.
5. Manual smoke: `python -m retail_agent.bq "SELECT ... LIMIT 5"` documented in WORKLOG.
6. Commits: `build: scaffold retail-agent package (task 0002)`, `feat(bq): add guarded BigQuery runner (task 0002)`.
