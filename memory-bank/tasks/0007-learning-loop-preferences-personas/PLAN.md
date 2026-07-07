# Plan — Task 0007

## Decisions

- Deterministic preference phrases only (tables / bullets / prose); no LLM classification.
- `/persona <name>` is a CLI-session/thread override; env `RETAIL_AGENT_PERSONA` remains default.
- Persona files hot-read on every `compose_report` turn.

## Steps

1. Extend `stores.py` with `preferences` table (same SQLite as reports).
2. Add `preferences` guard route + `preferences_router` node.
3. Add `personas/` seed files + `personas.py` loader.
4. Inject prefs/persona into `compose_report`; CLI `/prefs` and `/persona`.
5. Tests for persistence, isolation, prompt injection, hot-reload.
6. Version `0.6.0`, docs, handoff, commit.
