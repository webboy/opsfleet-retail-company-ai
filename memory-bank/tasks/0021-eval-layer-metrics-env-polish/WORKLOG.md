# Worklog — Task 0021

<!-- Append entries as work happens. Newest at the bottom. -->

## 2026-07-08

- Task created from the second deep-review pass. All four items verified: `--layer safety` exit code 1 with 11 phantom regressions; `self_heal_events=27` vs far fewer real heal turns; stale SQL/trios in `trace` output of a reports turn; `RETAIL_AGENT_PERSONA=formal` shell override ignored in favor of `.env`.
- Implementation started: baseline layer filter, per-turn self-heal metric, trace snapshot guard, env precedence fix.
- Implemented all four fixes; pytest 189, dry-run eval 16/16 and `--layer safety` 5/5 exit 0; version **0.19.0**; task set to `pending_review`.
- User approved 2026-07-08 — task marked **done**.
