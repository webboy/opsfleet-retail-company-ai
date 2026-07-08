# Task 0019 — Golden Bucket robustness: one malformed trio file crashes the CLI

## Metadata

- **Task ID**: 0019
- **Title**: Golden Bucket robustness: one malformed trio file crashes the CLI
- **Status**: done
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

The Golden Bucket is a runtime-editable asset curated by analysts
("assets over code"). But `TrioStore.__init__` → `load_trios` →
`load_trio_file` propagates any parse failure, so a single malformed
`golden_bucket/*.md` file kills `retail-agent` at startup with a raw Python
traceback — violating the "no crashes, no stack traces" principle and making
the whole agent hostage to one bad analyst edit.

## Reproduction (confirmed 2026-07-08)

```bash
printf -- "---\nquestion: broken\nsql: SELECT 1\n---\nbody" > golden_bucket/zz-broken.md
retail-agent --user demo
# -> Traceback ... load_trio_file ... KeyError: 'id'
```

Failure modes by file content:

- missing `id`/`question`/`sql` key → `KeyError` (uncaught traceback)
- invalid YAML front matter → `yaml.ParserError` (uncaught traceback)
- missing front matter → `ValueError` (caught by CLI `main`, prints `ERROR: ...` and exits — no chat)

The same fragility affects the MCP server (`TrioStore()` in
`retrieve_trios_handler`) and the eval runner (copies the bucket).

## Scope

- `load_trios`: wrap per-file loading; on failure, log a clear warning with
  the file path and reason, **skip the file**, and continue loading the rest.
- Surface the skip in observability (log line is enough for the prototype).
- Keep `load_trio_file` strict (raising) for direct/curation use; robustness
  lives in the directory-level loader.

### Out of scope

- Schema validation tooling / linting for trio files (candidate for a
  curation pipeline in production docs).

## Acceptance criteria

- [x] A bucket with one broken file (each of the three failure modes) still loads the remaining trios; CLI starts and answers.
- [x] Warning log names the offending file and reason.
- [x] MCP `retrieve_trios` keeps working with a broken file present.
- [x] New unit tests in `tests/test_golden.py` for the skip behavior.

## References

- `src/retail_agent/golden.py` (`load_trios`, `load_trio_file`, `TrioStore`)
- `docs/USAGE.md` (Adding a trio), `memory-bank/systemPatterns.md` ("Every failure path has a user-facing sentence", "Assets over code")
