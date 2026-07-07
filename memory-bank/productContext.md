# Product Context

## Why this project exists

Retail executives (Store / Regional Managers) are non-technical but need answers that today require a data analyst: cross-branch comparisons, revenue trends, inventory questions. The turnaround through human analysts is slow and expensive. The company already has two underused assets:

1. A read-only SQL warehouse with raw transaction logs.
2. Years of analyst work captured as **Trios** (Question → SQL → Report) — the "Golden Knowledge" Bucket.

The agent turns those assets into a self-service conversational analyst.

## Who uses it

- **Store Managers / Regional Managers** — ask questions, read reports, save/delete their own reports. Non-technical; must never see raw SQL errors or PII.
- **CEO / business owners** — set the tone/persona of reports (weekly, without developers).
- **Data analysts (curators)** — review and promote new Trios into the Golden Bucket (the learning loop).
- **Platform/ML engineers** — operate, observe, evaluate and extend the system.

## How it should work (user experience)

- Manager opens the chat (prototype: CLI) and asks a question in plain language.
- The agent understands the question **the way an analyst would** — grounded in similar historical Trios — generates SQL, runs it, and returns a short analyst-style report in the manager's preferred format (tables vs. bullets).
- Failures are invisible: bad SQL is retried and repaired internally; if the agent truly cannot answer, it says so gracefully and suggests a rephrase — never a stack trace.
- PII (customer emails/phones) **never** appears in output, period.
- Reports can be saved to a personal library. Deleting reports is conversational but guarded: the agent lists exactly what will be deleted and requires explicit confirmation; users can only delete their own reports.
- Off-topic or malicious requests ("ignore your instructions...", "drop table...") are politely refused.

## Product lens — start from the user moment

The system is judged by a specific moment: *a Regional Manager, five minutes before a call, asks why branch X is underperforming — and gets something they can act on.* Everything is built backwards from that moment, not forwards from a feature list.

Consequences:

- **Reports guide decisions, not display information.** Every report leads with the direct answer/key insight, then the supporting numbers, then — when warranted — what to look at next. A table dump without a "so what" is a failed report even if the SQL was perfect.
- **Workflows over features.** The capabilities (ask → follow up → save → preferences → guarded delete) matter as one continuous working session of a manager, and that is how they are demonstrated and documented — not as isolated feature demos.
- **Quality is measured against intent** (does the report answer what the user meant, is it actionable), not against "did the pipeline run".

## Product qualities

- **Trustworthy**: grounded in expert-approved query patterns, honest when unsure.
- **Safe**: PII-blind output, read-only data access, guarded destructive actions.
- **Adaptive**: learns formats per user, improves system-wide as new Trios are curated.
- **Governable**: report tone is a runtime-editable prompt asset, not code.
- **Extendable**: adding graph generation, e-mail delivery, or a new data source must be a new tool/node, not a rewrite.
