# Handoff — Task 0019

## Summary

Made Golden Bucket loading resilient: `load_trios()` now skips malformed `*.md` files with a warning instead of crashing CLI/MCP/eval startup. `load_trio_file()` remains strict for direct curation use.

## Changed files

- `src/retail_agent/golden.py` — per-file try/except in `load_trios()` with warning logs
- `tests/test_golden.py` — skip tests for missing id, bad YAML, no front matter; TrioStore startup test
- `tests/test_mcp_server.py` — MCP retrieve with malformed file present
- `docs/USAGE.md` — note that malformed trios are skipped with a warning
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.17.0**
- `memory-bank/tasks/0019-trio-file-robust-loading/*` — task docs
- `memory-bank/activeContext.md`, `memory-bank/progress.md`

## Impact

- One bad analyst edit no longer kills the whole agent.
- Valid trios continue to load and retrieve; broken files are logged for curation.
- No change to trio file format or retrieval logic for valid files.

## How to verify

```bash
pytest tests/test_golden.py tests/test_mcp_server.py -q
pytest -q
python -m retail_agent.evals
```

Optional manual sanity:

```bash
printf -- "---\nquestion: broken\nsql: SELECT 1\n---\nbody" > golden_bucket/zz-broken.md
retail-agent --user demo
# Ask an analysis question; CLI should start, logs should warn about zz-broken.md
rm golden_bucket/zz-broken.md
```

## Risks / rollback

- **Low risk**: only affects directory-level loading; strict `load_trio_file()` preserved.
- **Rollback**: revert commit; malformed files will again crash startup.

## Acceptance criteria check

- [x] Broken file modes (missing id, bad YAML, no front matter) skip file; valid trios load.
- [x] Warning log names offending file and reason (caplog tests).
- [x] MCP `retrieve_trios` works with broken file present.
- [x] Unit tests in `test_golden.py` and MCP test added.
