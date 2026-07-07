# Handoff — Task 0007

## Summary

Implemented per-user output preferences (SQLite), deterministic preference routing, hot-reloaded persona files, and CLI commands for viewing preferences and switching persona for the current session.

## Changed files

- `src/retail_agent/stores.py` — `preferences` table, get/set, format helpers
- `src/retail_agent/safety.py` — preference command parsing and `preferences` guard route
- `src/retail_agent/nodes/preferences_router.py` — save/show preference flows
- `src/retail_agent/personas.py` — hot-read persona loader
- `personas/default.md`, `personas/formal.md`, `personas/punchy.md` — seed personas
- `src/retail_agent/nodes/compose_report.py` — inject prefs + persona into system prompt
- `src/retail_agent/nodes/input_guard.py`, `state.py`, `graph.py` — preferences branch wiring
- `src/retail_agent/config.py`, `deps.py`, `cli.py` — personas dir env + `/prefs` + `/persona`
- `tests/test_preferences_store.py`, `tests/test_preferences_graph.py`, `tests/test_personas.py`, `tests/test_safety.py`
- `docs/TECHNICAL_EXPLANATION.md`, `.env.example`
- `pyproject.toml`, `src/retail_agent/__init__.py` — version `0.6.0`

## Impact

- Preferences share the same SQLite file as saved reports (`RETAIL_AGENT_DB_PATH`).
- Optional env: `RETAIL_AGENT_PERSONAS_DIR` (default `./personas`).
- `/persona <name>` applies only to the current CLI session/thread; `.env` default unchanged.
- Version bumped **0.5.0 → 0.6.0**.

## How to verify

1. `pytest -q` — expect **88 passed**.
2. CLI smoke:
   - `python -m retail_agent.cli --user alice --thread prefs-test`
   - `I prefer tables from now on` → acknowledgment saved
   - `/prefs` → shows Alice's format preference
   - Ask an analytics question → report prompt uses table formatting guidance
   - `/persona punchy` → session tone switches
   - Edit `personas/punchy.md` → next report uses updated tone without restart

## Risks / rollback

- Preference phrases are deterministic and may miss unusual wording until expanded.
- Persona/session override is not persisted across CLI restarts (by design).
- Rollback: revert commit and remove any new preference rows from SQLite if needed.

## Acceptance criteria check

- [x] "I prefer tables" as Alice persists and affects later reports; Bob unaffected; survives restart
- [x] Editing persona file changes next answer tone without CLI restart
- [x] pytest green for prefs, isolation, prompt injection, and persona hot-reload
