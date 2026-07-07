# Task 0007 — Learning loop: user preferences & personas

## Metadata

- **Task ID**: 0007
- **Title**: Learning loop: user preferences & personas
- **Status**: pending_review
- **Owner**: Engineer
- **Created**: 2026-07-07
- **Updated**: 2026-07-07

## Goal

Requirement 4a (per-user format preferences) and Requirement 8 (persona/tone editable by non-developers without redeployment). Requirement 4b (system learning) is covered by trio candidate capture from task 0004 + the HLD curation story.

## Scope

- **User preferences**: `preferences` table in SQLite (`user_id → output_format` (table/bullets/prose), plus free-form notes). Detection: when the user expresses a preference ("I prefer tables", "give me bullet points from now on"), persist it; every `compose_report` call injects the stored preference. Explicit command `/prefs` shows current ones.
- **Personas**: `personas/*.yaml|md` files (e.g. `default.md`, `formal.md`, `punchy.md`) containing tone instructions; selected via `RETAIL_AGENT_PERSONA` env or `/persona <name>` at runtime; file content is **re-read on every turn** — editing the file changes the very next answer, no restart.
- Tests: preference persistence + injection (mocked LLM asserting the pref text lands in the prompt); persona hot-reload (edit file between two turns in a test).

### Out of scope

- Analyst curation pipeline implementation (documented in HLD, seam exists via 0004 candidates).

## Acceptance criteria

- [ ] "I prefer tables" as `alice` → subsequent reports for alice render as tables; `bob` unaffected; survives CLI restart.
- [ ] Editing `personas/default.md` changes the tone of the next answer without restarting the CLI.
- [ ] pytest green for prefs and hot-reload.

## References

- Requirements 4, 8; `systemPatterns.md` D7, D8.
