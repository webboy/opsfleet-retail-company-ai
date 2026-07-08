# Handoff — Task 0027

## Summary

Hardened Golden Bucket retrieval and learning-loop candidate capture. Keyword fallback now returns no trios when there is zero token overlap (instead of arbitrary top-k examples). Candidate capture requires a fully composed analysis report via `report_complete=True`; budget-exhausted compose messages no longer enter the candidate queue.

## Changed files

- `src/retail_agent/golden.py` — zero-overlap keyword fallback returns empty list
- `src/retail_agent/state.py` — `report_complete` state field
- `src/retail_agent/nodes/compose_report.py` — set `report_complete` on success vs budget exhaustion
- `src/retail_agent/nodes/capture_candidate.py` — gate capture on `report_complete`
- `tests/test_golden.py`, `tests/test_golden_graph.py` — regression tests
- `docs/ARCHITECTURE.md`, `docs/TECHNICAL_EXPLANATION.md`, `docs/USAGE.md` — retrieval/capture policy
- `pyproject.toml`, `src/retail_agent/__init__.py` — version **0.23.0**
- `memory-bank/tasks/0027-golden-learning-hardening/*`, `INDEX.md`, `activeContext.md`, `progress.md`

## Impact

- Fewer irrelevant few-shot examples injected into SQL prompts when embedding API is down and keyword overlap is zero.
- Cleaner candidate JSONL queue — incomplete compose-budget messages are excluded.
- Embedding retrieval documented as best-effort and separate from per-turn LLM call budget (no runtime budget wiring in this task).

## How to verify

1. Targeted tests:
   ```bash
   pytest tests/test_golden.py tests/test_golden_graph.py -q
   ```
2. Full gate:
   ```bash
   pytest -q
   python -m retail_agent.evals
   ```
3. Docs separation:
   ```bash
   rg "memory-bank|task 0" README.md docs/
   ```

## Risks / rollback

- Low risk. Revert commit to restore arbitrary keyword fallback and prior capture gating.

## Acceptance criteria check

- [x] Keyword fallback returns empty retrieval when all candidate scores are zero
- [x] SQL generation prompt handles no retrieved trios cleanly (existing empty prompt text)
- [x] Candidate capture skipped for budget-exhausted/incomplete report states
- [x] Tests cover zero-overlap retrieval and capture gating
- [x] Docs distinguish automatic candidate capture from manual Golden Bucket promotion
- [x] `pytest -q` and `python -m retail_agent.evals` pass
