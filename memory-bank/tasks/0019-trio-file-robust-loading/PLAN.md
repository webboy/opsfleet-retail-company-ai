# Plan — Task 0019

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. In `load_trios`, wrap `load_trio_file(path)` in `try/except Exception`; log `logger.warning("Skipping invalid trio file %s: %s", path, exc)` and continue.
2. Tests: bucket with valid + broken files (missing id, bad YAML, no front matter) → only valid trios load; assert warning logged (caplog).
3. Manual check: broken file in `golden_bucket/`, CLI starts, `[retrieved trios=...]` still works.
4. Docs: add a sentence to `docs/USAGE.md` (Adding a trio) that malformed files are skipped with a logged warning.
5. Commit: `fix(golden): skip malformed trio files instead of crashing (task 0019)` + minor version bump.
