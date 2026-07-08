"""Tests for CLI diagnostic rendering."""

from __future__ import annotations

import pandas as pd
import pytest
from langchain_core.messages import HumanMessage

from retail_agent.bq import QueryResult
from retail_agent.cli import _should_print_analysis_diagnostics
from retail_agent.deps import AgentDeps
from retail_agent.graph import compile_graph
from retail_agent.stores import ReportStore
from tests.helpers import make_settings
from tests.test_graph import FakeBQRunner, ScriptLLM

GOOD_SQL = (
    "SELECT order_id FROM `bigquery-public-data.thelook_ecommerce.orders` LIMIT 5"
)


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        ({"guard_route": "analysis", "sql": "SELECT 1"}, True),
        ({"guard_route": "reports", "sql": "SELECT 1", "retrieved_trio_ids": ["monthly-revenue"]}, False),
        ({"guard_route": "preferences"}, False),
        ({"guard_route": "schema"}, False),
        ({"guard_route": "chitchat"}, False),
    ],
)
def test_should_print_analysis_diagnostics(result, expected):
    assert _should_print_analysis_diagnostics(result) is expected


@pytest.fixture
def settings(tmp_path):
    return make_settings(
        google_api_key="test-key",
        reports_db_path=str(tmp_path / "reports.sqlite3"),
    )


@pytest.fixture
def deps(settings):
    llm = ScriptLLM(["unused"])
    bq = FakeBQRunner([])
    report_store = ReportStore(db_path=settings.reports_db_path)
    return AgentDeps(settings=settings, llm=llm, bq_runner=bq, report_store=report_store)


def _thread_config(thread_id: str):
    return {"configurable": {"thread_id": thread_id}}


def _seed_analysis_turn(deps: AgentDeps, *, thread_id: str = "cli-diag-thread"):
    llm = ScriptLLM([f"```sql\n{GOOD_SQL}\n```", "Revenue grew 12% in Q1."])
    bq = FakeBQRunner(
        [QueryResult(ok=True, dataframe=pd.DataFrame({"order_id": [1]}), sql=GOOD_SQL)]
    )
    analysis_deps = AgentDeps(
        settings=deps.settings,
        llm=llm,
        bq_runner=bq,
        report_store=deps.report_store,
    )
    graph = compile_graph(analysis_deps)
    config = _thread_config(thread_id)
    result = graph.invoke(
        {
            "messages": [HumanMessage(content="How did revenue trend?")],
            "user_id": "alice",
            "question": "How did revenue trend?",
        },
        config,
    )
    assert result["guard_route"] == "analysis"
    assert result.get("sql")
    return graph, config, result


def test_non_analysis_turn_does_not_qualify_for_diagnostics(deps):
    graph, config, analysis_result = _seed_analysis_turn(deps)

    list_result = graph.invoke(
        {
            "messages": [HumanMessage(content="show my reports")],
            "user_id": "alice",
            "question": "show my reports",
        },
        config,
    )

    assert analysis_result.get("sql")
    assert list_result["guard_route"] == "reports"
    assert _should_print_analysis_diagnostics(list_result) is False


def test_save_turn_after_analysis_does_not_qualify_for_diagnostics(deps):
    graph, config, _ = _seed_analysis_turn(deps)

    save_result = graph.invoke(
        {
            "messages": [HumanMessage(content="save this report")],
            "user_id": "alice",
            "question": "save this report",
        },
        config,
    )

    assert save_result["guard_route"] == "reports"
    assert _should_print_analysis_diagnostics(save_result) is False


def test_prefs_turn_after_analysis_does_not_qualify_for_diagnostics(deps):
    graph, config, _ = _seed_analysis_turn(deps)

    prefs_result = graph.invoke(
        {
            "messages": [HumanMessage(content="show my preferences")],
            "user_id": "alice",
            "question": "show my preferences",
        },
        config,
    )

    assert prefs_result["guard_route"] == "preferences"
    assert _should_print_analysis_diagnostics(prefs_result) is False
