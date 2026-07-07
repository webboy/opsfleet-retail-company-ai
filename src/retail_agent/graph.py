"""LangGraph wiring for the retail analysis agent."""

from __future__ import annotations

from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from retail_agent.deps import AgentDeps
from retail_agent.nodes.answer_schema import answer_schema
from retail_agent.nodes.compose_report import compose_report
from retail_agent.nodes.execute_bq import execute_bq
from retail_agent.nodes.fallback_answer import fallback_answer
from retail_agent.nodes.generate_sql import generate_sql
from retail_agent.nodes.route_turn import route_turn
from retail_agent.state import AgentState


def build_graph(deps: AgentDeps):
    graph = StateGraph(AgentState)

    graph.add_node("route_turn", lambda state: route_turn(state, deps))
    graph.add_node("answer_schema", lambda state: answer_schema(state, deps))
    graph.add_node("generate_sql", lambda state: generate_sql(state, deps))
    graph.add_node("execute_bq", lambda state: execute_bq(state, deps))
    graph.add_node("compose_report", lambda state: compose_report(state, deps))
    graph.add_node("fallback_answer", fallback_answer)

    graph.add_edge(START, "route_turn")
    graph.add_conditional_edges(
        "route_turn",
        _route_after_turn,
        {"schema": "answer_schema", "analysis": "generate_sql"},
    )
    graph.add_edge("answer_schema", END)
    graph.add_conditional_edges(
        "generate_sql",
        _route_after_generate,
        {"execute": "execute_bq", "fallback": "fallback_answer"},
    )
    graph.add_conditional_edges(
        "execute_bq",
        _route_after_execute,
        {
            "report": "compose_report",
            "retry": "generate_sql",
            "fallback": "fallback_answer",
        },
    )
    graph.add_edge("compose_report", END)
    graph.add_edge("fallback_answer", END)

    return graph


def compile_graph(deps: AgentDeps | None = None, *, checkpointer: MemorySaver | None = None):
    deps = deps or AgentDeps.create()
    checkpointer = checkpointer or MemorySaver()
    return build_graph(deps).compile(checkpointer=checkpointer)


def _route_after_turn(state: AgentState) -> Literal["schema", "analysis"]:
    if state.get("turn_mode") == "schema":
        return "schema"
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
