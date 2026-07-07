"""LangGraph wiring for the retail analysis agent."""

from __future__ import annotations

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
from retail_agent.nodes.reports_router import reports_router
from retail_agent.nodes.retrieve_trios import retrieve_trios
from retail_agent.nodes.route_turn import route_turn
from retail_agent.state import AgentState


def build_graph(deps: AgentDeps):
    graph = StateGraph(AgentState)

    graph.add_node("input_guard", lambda state: input_guard(state, deps))
    graph.add_node("route_turn", lambda state: route_turn(state, deps))
    graph.add_node("answer_chitchat", answer_chitchat)
    graph.add_node("answer_schema", lambda state: answer_schema(state, deps))
    graph.add_node("retrieve_trios", lambda state: retrieve_trios(state, deps))
    graph.add_node("generate_sql", lambda state: generate_sql(state, deps))
    graph.add_node("execute_bq", lambda state: execute_bq(state, deps))
    graph.add_node("pii_mask", lambda state: pii_mask(state, deps))
    graph.add_node("compose_report", lambda state: compose_report(state, deps))
    graph.add_node("output_mask", lambda state: output_mask(state, deps))
    graph.add_node("capture_candidate", lambda state: capture_candidate(state, deps))
    graph.add_node("fallback_answer", fallback_answer)
    graph.add_node("reports_router", lambda state: reports_router(state, deps))

    graph.add_edge(START, "input_guard")
    graph.add_conditional_edges(
        "input_guard",
        _route_after_guard,
        {
            "allowed": "route_turn",
            "refused": "fallback_answer",
            "reports": "reports_router",
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
    graph.add_edge("fallback_answer", END)

    return graph


def compile_graph(deps: AgentDeps | None = None, *, checkpointer: MemorySaver | None = None):
    deps = deps or AgentDeps.create()
    checkpointer = checkpointer or MemorySaver()
    return build_graph(deps).compile(checkpointer=checkpointer)


def _route_after_guard(state: AgentState) -> Literal["allowed", "refused", "reports"]:
    if state.get("guard_decision") == "refused":
        return "refused"
    if state.get("guard_route") == "reports":
        return "reports"
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
