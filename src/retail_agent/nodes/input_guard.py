"""Classify and guard user input before the main agent pipeline."""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from retail_agent.deps import AgentDeps, resolve_budget
from retail_agent.llm import (
    BudgetExhaustedError,
    CallBudget,
    invoke_with_retry,
    is_quota_exhausted_error,
    quota_exhausted_message,
)
from retail_agent.safety import (
    InputPrecheck,
    classify_input_precheck,
    parse_llm_guard_label,
    parse_report_command,
    refusal_message,
)
from retail_agent.state import AgentState

logger = logging.getLogger(__name__)


def input_guard(state: AgentState, deps: AgentDeps) -> dict:
    question = state.get("question") or _latest_user_message(state)
    precheck = classify_input_precheck(question)
    budget = resolve_budget(state, deps)

    if precheck.decision == "refused":
        logger.info("Input guard refused turn route=%s reason=%s", precheck.route, precheck.reason)
        return _refused_update(question, precheck)

    if precheck.needs_llm:
        precheck = _llm_classify(question, deps, budget, precheck)
        if precheck.decision == "refused":
            logger.info("Input guard refused turn route=%s reason=%s", precheck.route, precheck.reason)
            return _refused_update(question, precheck)

    logger.info("Input guard allowed turn route=%s reason=%s", precheck.route, precheck.reason)
    update: dict = {
        "question": question,
        "guard_decision": "allowed",
        "guard_route": precheck.route,
        "guard_reason": precheck.reason,
        "pii_note_required": precheck.pii_sensitive,
        "llm_budget": budget.to_dict(),
        "status": "running",
    }
    if precheck.route == "reports":
        report_cmd = parse_report_command(question)
        if report_cmd:
            update["report_action"] = report_cmd.action
            update["report_selector_kind"] = report_cmd.selector_kind
            update["report_mention"] = report_cmd.mention
    return update


def _llm_classify(
    question: str,
    deps: AgentDeps,
    budget: CallBudget,
    precheck: InputPrecheck,
) -> InputPrecheck:
    try:
        response = invoke_with_retry(
            deps.llm,
            [
                SystemMessage(
                    content=(
                        "Classify the user message for a retail analytics assistant. "
                        "Reply with exactly one label: analysis, schema, chitchat, "
                        "off_topic, or malicious."
                    )
                ),
                HumanMessage(content=question),
            ],
            budget,
            max_retries=1,
        )
        route = parse_llm_guard_label(str(response.content))
    except BudgetExhaustedError:
        route = precheck.route
    except Exception as exc:
        if is_quota_exhausted_error(exc):
            logger.warning("Input guard LLM classify skipped: quota exhausted")
            route = precheck.route
        else:
            raise

    if route in {"malicious", "off_topic"}:
        return InputPrecheck(
            decision="refused",
            route=route,
            reason=f"llm classified as {route}",
            pii_sensitive=precheck.pii_sensitive,
        )

    return InputPrecheck(
        decision="allowed",
        route=route if route in {"analysis", "schema", "chitchat"} else "analysis",
        reason=f"llm classified as {route}",
        pii_sensitive=precheck.pii_sensitive,
    )


def _refused_update(question: str, precheck: InputPrecheck) -> dict:
    return {
        "question": question,
        "guard_decision": "refused",
        "guard_route": precheck.route,
        "guard_reason": precheck.reason,
        "report": refusal_message(precheck.route),
        "status": "fallback",
    }


def _latest_user_message(state: AgentState) -> str:
    messages = state.get("messages") or []
    for message in reversed(messages):
        if getattr(message, "type", "") == "human":
            return str(message.content)
    return ""
