# Plan — Task 0018

> Update this plan before starting implementation (see `task-folder-workflow.mdc`).

1. Add `last_analysis_report`, `last_analysis_question`, `last_analysis_sql` to `AgentState`; `output_mask` (end of the analysis pipeline) writes them when `status=done` and `turn_mode=analysis`.
2. `_save_report` reads only those fields; remove the message-history scan for the title.
3. Guard message when the fields are absent.
4. Tests: three scenarios from TASK.md as graph tests in `tests/test_reports_graph.py`.
5. Docs: `docs/USAGE.md` wording for `/save` already says "most recent report" — now true; note in WORKLOG.
6. Commit: `fix(reports): save the last analysis report, not the last answer (task 0018)` + minor version bump.
