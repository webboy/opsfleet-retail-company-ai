"""Handle user output preference show and update flows."""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage

from retail_agent.deps import AgentDeps
from retail_agent.safety import PreferenceCommand, parse_preference_command
from retail_agent.state import AgentState
from retail_agent.stores import format_preferences_summary

logger = logging.getLogger(__name__)


def preferences_router(state: AgentState, deps: AgentDeps) -> dict:
    user_id = state.get("user_id") or ""
    question = state.get("question") or ""
    command = parse_preference_command(question)
    if command is None:
        command = _command_from_state(state)
        if command is None:
            return _done("I didn't understand that preference request.")

    if command.action == "show":
        return _show_preferences(deps, user_id)
    return _set_preference(deps, user_id, command)


def _show_preferences(deps: AgentDeps, user_id: str) -> dict:
    prefs = deps.report_store.get_preferences(user_id)
    summary = format_preferences_summary(prefs)
    return _done(f"Your saved preferences:\n{summary}")


def _set_preference(deps: AgentDeps, user_id: str, command: PreferenceCommand) -> dict:
    if not command.output_format:
        return _done("Please specify a format such as tables, bullet points, or prose.")

    saved = deps.report_store.set_output_format(
        user_id,
        command.output_format,
        notes=command.notes,
    )
    logger.info(
        "Saved preference user=%s format=%s",
        user_id,
        saved.output_format,
    )
    return _done(
        f"Saved your preference: future reports will use {saved.output_format} formatting."
    )


def _command_from_state(state: AgentState) -> PreferenceCommand | None:
    action = state.get("preference_action")
    if not action:
        return None
    return PreferenceCommand(
        action=action,  # type: ignore[arg-type]
        output_format=state.get("preference_output_format"),
    )


def _done(report: str) -> dict:
    return {
        "report": report,
        "status": "done",
        "messages": [AIMessage(content=report)],
    }
