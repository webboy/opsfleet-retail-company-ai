# Plan — Task 0008

1. `observability.py`: `TurnTracer` (context-managed per node) writing JSONL; integrate into all graph nodes.
2. `trace` and `metrics` CLI entry points reading the JSONL.
3. Optional LangSmith wiring (env-gated).
4. `evals/cases.yaml`: ~15–20 capability cases + safety cases; assertion engine (properties, not exact values — dataset is rolling).
5. LLM-as-judge layer: judge prompt asset, structured 1–5 score + rationale output, JSONL persistence of runs, baseline comparison + regression flagging.
6. Eval runner module with pass/fail + score table output.
7. Tests on synthetic event streams and recorded turns; judge mocked.
8. Version minor bump. Commits: `feat(obs): add structured tracing and metrics (task 0008)`, `feat(evals): add QA evaluation suite with intent scoring (task 0008)`.
