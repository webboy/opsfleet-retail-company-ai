"""Handle saved report save, list, and guarded delete flows."""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from retail_agent.deps import AgentDeps
from retail_agent.safety import parse_report_command
from retail_agent.state import AgentState
from retail_agent.stores import (
    ReportSelector,
    format_candidate_list,
    format_report_summary,
    is_delete_confirmed,
)

logger = logging.getLogger(__name__)


def reports_router(state: AgentState, deps: AgentDeps) -> dict:
    user_id = state.get("user_id") or ""
    question = state.get("question") or ""
    command = parse_report_command(question)
    if command is None:
        command_action = state.get("report_action")
        if not command_action:
            return _done("I didn't understand that report request.")
        command = _command_from_state(state)

    if command.action == "save":
        return _save_report(state, deps, user_id)
    if command.action == "list":
        return _list_reports(deps, user_id)
    return _delete_reports(state, deps, user_id, command)


def _list_reports(deps: AgentDeps, user_id: str) -> dict:
    reports = deps.report_store.list_reports(user_id)
    if not reports:
        return _done("You don't have any saved reports yet.")

    body = "\n".join(format_report_summary(report) for report in reports)
    return _done(f"Your saved reports:\n{body}")


def _save_report(state: AgentState, deps: AgentDeps, user_id: str) -> dict:
    report = state.get("last_analysis_report")
    if not report:
        return _done(
            "There is no recent report to save yet. Ask an analytics question first, "
            "then say \"save this report\" or use /save."
        )

    source_question = state.get("last_analysis_question") or ""
    title = _title_from_question(source_question or "Saved report")
    saved = deps.report_store.save_report(
        owner=user_id,
        title=title,
        content=report,
        question=source_question or None,
        sql=state.get("last_analysis_sql"),
    )
    logger.info("Saved report id=%s owner=%s", saved.id, user_id)
    return _done(f"Saved report \"{saved.title}\" to your library.")


def _delete_reports(state: AgentState, deps: AgentDeps, user_id: str, command) -> dict:
    selector = ReportSelector(kind=command.selector_kind or "all", mention=command.mention)
    candidates = deps.report_store.find_reports(user_id, selector)
    if not candidates:
        return _done("I couldn't find any of your saved reports that match that request.")

    summary = format_candidate_list(candidates)
    prompt = (
        "I found the following saved reports that match your delete request:\n"
        f"{summary}\n\n"
        "Reply yes or confirm to delete them, or anything else to cancel."
    )
    confirmation = interrupt(
        {
            "prompt": prompt,
            "report_ids": [report.id for report in candidates],
            "owner": user_id,
        }
    )

    if not is_delete_confirmed(confirmation):
        return _done("Deletion cancelled. Your reports were not changed.")

    deleted = deps.report_store.delete_reports(
        user_id,
        [report.id for report in candidates],
    )
    logger.info("Deleted %s reports for owner=%s", deleted, user_id)
    return _done(f"Deleted {deleted} saved report(s).")


def _command_from_state(state: AgentState):
    from retail_agent.safety import ReportCommand

    return ReportCommand(
        action=state.get("report_action"),  # type: ignore[arg-type]
        selector_kind=state.get("report_selector_kind"),
        mention=state.get("report_mention"),
    )


def _title_from_question(question: str) -> str:
    cleaned = question.strip()
    if not cleaned:
        return "Saved report"
    if len(cleaned) <= 80:
        return cleaned
    return cleaned[:77] + "..."


def _done(report: str) -> dict:
    return {
        "report": report,
        "status": "done",
        "messages": [AIMessage(content=report)],
    }
