"""LangGraph wiring for the retail analysis agent."""

from __future__ import annotations

import os
from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from retail_agent.deps import AgentDeps
from retail_agent.nodes.answer_chitchat import answer_chitchat
from retail_agent.nodes.answer_schema import answer_schema
from retail_agent.nodes.capture_candidate import capture_candidate
from retail_agent.nodes.compose_report import compose_report
from retail_agent.nodes.execute_bq import execute_bq
from retail_agent.nodes.fallback_answer import fallback_answer
from retail_agent.nodes.generate_sql import generate_sql
from retail_agent.nodes.input_guard import input_guard
from retail_agent.nodes.output_mask import output_mask
from retail_agent.nodes.pii_mask import pii_mask
from retail_agent.nodes.preferences_router import preferences_router
from retail_agent.nodes.reports_router import reports_router
from retail_agent.nodes.retrieve_trios import retrieve_trios
from retail_agent.nodes.route_turn import route_turn
from retail_agent.observability import traced_node
from retail_agent.state import AgentState


def build_graph(deps: AgentDeps):
    graph = StateGraph(AgentState)

    graph.add_node("input_guard", traced_node("input_guard", input_guard, deps))
    graph.add_node("route_turn", traced_node("route_turn", route_turn, deps))
    graph.add_node("answer_chitchat", traced_node("answer_chitchat", answer_chitchat, deps, needs_deps=False))
    graph.add_node("answer_schema", traced_node("answer_schema", answer_schema, deps))
    graph.add_node("retrieve_trios", traced_node("retrieve_trios", retrieve_trios, deps))
    graph.add_node("generate_sql", traced_node("generate_sql", generate_sql, deps))
    graph.add_node("execute_bq", traced_node("execute_bq", execute_bq, deps))
    graph.add_node("pii_mask", traced_node("pii_mask", pii_mask, deps))
    graph.add_node("compose_report", traced_node("compose_report", compose_report, deps))
    graph.add_node("output_mask", traced_node("output_mask", output_mask, deps))
    graph.add_node("capture_candidate", traced_node("capture_candidate", capture_candidate, deps))
    graph.add_node("fallback_answer", traced_node("fallback_answer", fallback_answer, deps, needs_deps=False))
    graph.add_node("reports_router", traced_node("reports_router", reports_router, deps))
    graph.add_node("preferences_router", traced_node("preferences_router", preferences_router, deps))

    graph.add_edge(START, "input_guard")
    graph.add_conditional_edges(
        "input_guard",
        _route_after_guard,
        {
            "allowed": "route_turn",
            "refused": "fallback_answer",
            "reports": "reports_router",
            "preferences": "preferences_router",
        },
    )
    graph.add_conditional_edges(
        "route_turn",
        _route_after_turn,
        {"schema": "answer_schema", "analysis": "retrieve_trios", "chitchat": "answer_chitchat"},
    )
    graph.add_edge("answer_chitchat", END)
    graph.add_edge("answer_schema", END)
    graph.add_edge("retrieve_trios", "generate_sql")
    graph.add_conditional_edges(
        "generate_sql",
        _route_after_generate,
        {"execute": "execute_bq", "fallback": "fallback_answer"},
    )
    graph.add_conditional_edges(
        "execute_bq",
        _route_after_execute,
        {
            "report": "pii_mask",
            "retry": "generate_sql",
            "fallback": "fallback_answer",
        },
    )
    graph.add_edge("pii_mask", "compose_report")
    graph.add_edge("compose_report", "output_mask")
    graph.add_edge("output_mask", "capture_candidate")
    graph.add_edge("capture_candidate", END)
    graph.add_edge("reports_router", END)
    graph.add_edge("preferences_router", END)
    graph.add_edge("fallback_answer", END)

    return graph


def compile_graph(deps: AgentDeps | None = None, *, checkpointer: MemorySaver | None = None):
    deps = deps or AgentDeps.create()
    checkpointer = checkpointer or MemorySaver()
    _maybe_enable_langsmith()
    return build_graph(deps).compile(checkpointer=checkpointer)


def _maybe_enable_langsmith() -> None:
    if os.getenv("LANGSMITH_TRACING", "").lower() in {"1", "true", "yes"} and os.getenv("LANGSMITH_API_KEY"):
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")


def _route_after_guard(
    state: AgentState,
) -> Literal["allowed", "refused", "reports", "preferences"]:
    if state.get("guard_decision") == "refused":
        return "refused"
    if state.get("guard_route") == "reports":
        return "reports"
    if state.get("guard_route") == "preferences":
        return "preferences"
    return "allowed"


def _route_after_turn(state: AgentState) -> Literal["schema", "analysis", "chitchat"]:
    mode = state.get("turn_mode")
    if mode == "schema":
        return "schema"
    if mode == "chitchat":
        return "chitchat"
    return "analysis"


def _route_after_generate(state: AgentState) -> Literal["execute", "fallback"]:
    if state.get("status") == "fallback":
        return "fallback"
    return "execute"


def _route_after_execute(state: AgentState) -> Literal["report", "retry", "fallback"]:
    if state.get("status") == "fallback":
        return "fallback"

    attempts = state.get("sql_attempts", 0)
    max_attempts = state.get("max_sql_attempts", 3)

    if state.get("query_ok") and not state.get("query_empty"):
        return "report"

    if attempts < max_attempts:
        return "retry"

    return "fallback"
