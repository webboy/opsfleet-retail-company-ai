# Task 0020 — Preference regex hijacks analysis questions mentioning "table"

## Metadata

- **Task ID**: 0020
- **Title**: Preference regex hijacks analysis questions mentioning "table"
- **Status**: pending_review
- **Owner**: Engineer
- **Created**: 2026-07-08
- **Updated**: 2026-07-08

## Goal

`parse_preference_command` pattern `\b(?:i prefer|prefer|use)\b.*\btables?\b`
matches natural analysis phrasing that references database **tables**. The
guard routes such turns to `preferences_router`, silently overwrites the
user's saved output format, and never answers the actual question.

## Reproduction (confirmed 2026-07-08)

```
"Can I use the orders table to compute revenue?"   -> route=preferences, sets output_format=table
"use the users table to find top customers"       -> route=preferences, sets output_format=table
```

Both should be analysis turns. The user gets
"Saved your preference: future reports will use table formatting." instead of
an answer, and their stored preference is corrupted as a side effect.

## Scope

- Tighten preference patterns so they require **formatting intent**, e.g.:
  - anchor on format words in formatting context: "table format",
    "as a table", "in tables", "prefer tables", "tables from now on";
  - exclude phrases where "table" is followed/preceded by a DB-ish token
    (`the <name> table`, `orders table`, `users table`) or the sentence
    contains analysis markers.
- Apply the same review to bullet/prose patterns (`\bformat.*\btables?\b`
  style catch-alls).
- Preference-setting remains deterministic — no LLM in this path.

### Out of scope

- Full NLU for preferences; documented known-limitation phrasing stays.

## Acceptance criteria

- [x] Both reproduction sentences route to `analysis` and do not touch stored preferences.
- [x] Genuine preference phrases keep working: "I prefer tables from now on", "table format please", "give me bullet points from now on", "/prefs".
- [x] Existing preference tests green; new false-positive regression tests added.

## References

- `src/retail_agent/safety.py` (`_TABLE_PREFERENCE_PATTERNS`, `parse_preference_command`, `classify_input_precheck` ordering)
- `tests/test_safety.py`, `tests/test_preferences_graph.py`
- Requirement 4a (user-level preferences), `memory-bank/progress.md` known issue ("preference phrase detection may miss unusual phrasing" — this is the inverse: it catches too much)
