# Task 0006 — High-Stakes Oversight: saved reports & delete confirmation

## Metadata

- **Task ID**: 0006
- **Title**: High-Stakes Oversight: saved reports & delete confirmation
- **Status**: pending_review
- **Owner**: Engineer
- **Created**: 2026-07-07
- **Updated**: 2026-07-07

## Goal

Requirement 3: a "Saved Reports" library with conversational but strictly guarded destructive operations — deletes require explicit confirmation, and users can only delete their own reports.

## Scope

- `src/retail_agent/stores.py`: SQLite `reports` table (id, owner, title, content, created_at, tags/derived keywords).
- Report management flows routed by `input_guard` → `reports_router`:
  - **Save**: after an answer, "save this report" (or `/save`) persists it under the current user.
  - **List**: "show my reports".
  - **Delete**: natural-language selectors — "Delete all reports mentioning Client X", "Delete all the reports we made today" → resolve to a concrete candidate set **scoped to `owner = current_user`** → present the exact list (titles + dates) → **LangGraph `interrupt()`** → only explicit confirmation (`yes`/`confirm`) executes; anything else cancels. Empty candidate set → clear message, no interrupt.
- UX: confirmation is one natural chat turn (no separate mode/menus).
- Tests: selector resolution (mention/today filters), ownership isolation (user B's reports never in user A's candidate set nor deletable), interrupt flow (confirm deletes / decline keeps / gibberish cancels).

### Out of scope

- Report sharing, admin roles, soft-delete/undo (mention as production consideration in HLD).

## Acceptance criteria

- [ ] Save → list → delete-by-mention and delete-today flows work in the CLI for `--user alice` and are isolated from `--user bob`.
- [ ] No delete ever executes without an explicit confirmation reply to the listed candidate set.
- [ ] pytest green for selectors, ownership and confirmation state machine.

## References

- Requirement 3; `systemPatterns.md` D6; prototype requirement option (b).
