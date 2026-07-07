# Plan — Task 0005

## Policy

- Explicit PII requests (e.g. customer emails) may run as analysis, but output is always masked with a short PII policy note.
- Input guard: deterministic hard blocks first; small LLM fallback only for ambiguous turns.

## Steps

1. `safety.py`: `classify_input_precheck`, `mask_dataframe`, `mask_text`, masking metadata.
2. Nodes: `input_guard`, `pii_mask`, `output_mask`.
3. Graph: `START -> input_guard -> route_turn | fallback`; `execute_bq -> pii_mask -> compose_report -> output_mask -> capture_candidate`.
4. State: guard decision/reason, PII mask metadata, serialized result rows for masking.
5. Tests: unit + graph integration for guard refusals and end-to-end masking.
6. Version bump to `0.4.0`, docs, handoff, commit.
