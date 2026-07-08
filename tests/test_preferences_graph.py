"""Graph integration tests for user preferences and personas."""

from __future__ import annotations

import pandas as pd
import pytest
from langchain_core.messages import AIMessage, HumanMessage

from retail_agent.bq import QueryResult
from retail_agent.deps import AgentDeps
from retail_agent.graph import compile_graph
from retail_agent.nodes.compose_report import compose_report
from retail_agent.stores import ReportStore
from tests.helpers import make_settings
from tests.test_graph import FakeBQRunner, ScriptLLM

GOOD_SQL = (
    "SELECT order_id FROM `bigquery-public-data.thelook_ecommerce.orders` LIMIT 5"
)


class CapturingLLM:
    def __init__(self, response: str = "Report body"):
        self.response = response
        self.calls = 0
        self.last_messages = None

    def invoke(self, messages):
        self.calls += 1
        self.last_messages = messages
        return AIMessage(content=self.response)


@pytest.fixture
def settings(tmp_path):
    personas_dir = tmp_path / "personas"
    personas_dir.mkdir()
    (personas_dir / "default.md").write_text("Default persona instructions.", encoding="utf-8")
    (personas_dir / "punchy.md").write_text("Punchy persona instructions.", encoding="utf-8")
    return make_settings(
        google_api_key="test-key",
        reports_db_path=str(tmp_path / "agent.sqlite3"),
        personas_dir=str(personas_dir),
    )


@pytest.fixture
def deps(settings):
    llm = ScriptLLM(["unused"])
    bq = FakeBQRunner([])
    report_store = ReportStore(db_path=settings.reports_db_path)
    return AgentDeps(settings=settings, llm=llm, bq_runner=bq, report_store=report_store)


def _thread_config(thread_id: str = "prefs-thread"):
    return {"configurable": {"thread_id": thread_id}}


def test_preference_statement_persists_for_user(deps):
    graph = compile_graph(deps)

    result = graph.invoke(
        {
            "messages": [HumanMessage(content="I prefer tables from now on")],
            "user_id": "alice",
            "question": "I prefer tables from now on",
        },
        _thread_config("pref-set"),
    )

    assert "Saved your preference" in result["report"]
    prefs = deps.report_store.get_preferences("alice")
    assert prefs is not None
    assert prefs.output_format == "table"


def test_show_preferences_command(deps):
    deps.report_store.set_output_format("alice", "bullets")
    graph = compile_graph(deps)

    result = graph.invoke(
        {
            "messages": [HumanMessage(content="show my preferences")],
            "user_id": "alice",
            "question": "show my preferences",
        },
        _thread_config("pref-show"),
    )

    assert "Output format: bullets" in result["report"]


def test_bob_preferences_unaffected_by_alice(deps):
    graph = compile_graph(deps)

    graph.invoke(
        {
            "messages": [HumanMessage(content="I prefer tables from now on")],
            "user_id": "alice",
            "question": "I prefer tables from now on",
        },
        _thread_config("pref-isolation-alice"),
    )

    bob_prefs = deps.report_store.get_preferences("bob")
    assert bob_prefs is None


def test_database_table_question_does_not_overwrite_preferences(deps):
    deps.report_store.set_output_format("alice", "bullets")
    llm = ScriptLLM([f"```sql\n{GOOD_SQL}\n```", "Revenue summary"])
    bq = FakeBQRunner(
        [QueryResult(ok=True, dataframe=pd.DataFrame({"order_id": [1]}), sql=GOOD_SQL)]
    )
    graph = compile_graph(
        AgentDeps(
            settings=deps.settings,
            llm=llm,
            bq_runner=bq,
            report_store=deps.report_store,
        )
    )

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content="Can I use the orders table to compute revenue?")
            ],
            "user_id": "alice",
            "question": "Can I use the orders table to compute revenue?",
        },
        _thread_config("table-analysis-not-pref"),
    )

    prefs = deps.report_store.get_preferences("alice")
    assert prefs is not None
    assert prefs.output_format == "bullets"
    assert result["guard_route"] == "analysis"
    assert "Saved your preference" not in result["report"]


def test_compose_report_injects_table_preference(settings):
    llm = CapturingLLM()
    store = ReportStore(db_path=settings.reports_db_path)
    store.set_output_format("alice", "table")
    deps = AgentDeps(
        settings=settings,
        llm=llm,
        bq_runner=FakeBQRunner([]),
        report_store=store,
    )

    compose_report(
        {
            "user_id": "alice",
            "question": "Show top orders",
            "sql": GOOD_SQL,
            "result_preview": "order_id\n1",
            "llm_budget": {"max_calls": 8, "used": 0},
            "messages": [],
        },
        deps,
    )

    assert llm.last_messages is not None
    system_text = str(llm.last_messages[0].content)
    assert "markdown table" in system_text.lower()


def test_compose_report_hot_reloads_persona_file(settings):
    llm = CapturingLLM()
    deps = AgentDeps(
        settings=settings,
        llm=llm,
        bq_runner=FakeBQRunner([]),
        report_store=ReportStore(db_path=settings.reports_db_path),
    )
    persona_path = settings.personas_dir and __import__("pathlib").Path(settings.personas_dir) / "punchy.md"

    compose_report(
        {
            "user_id": "alice",
            "persona_name": "punchy",
            "question": "Show top orders",
            "sql": GOOD_SQL,
            "result_preview": "order_id\n1",
            "llm_budget": {"max_calls": 8, "used": 0},
            "messages": [],
        },
        deps,
    )
    first = str(llm.last_messages[0].content)

    persona_path.write_text("Updated punchy persona instructions.", encoding="utf-8")

    compose_report(
        {
            "user_id": "alice",
            "persona_name": "punchy",
            "question": "Show top orders",
            "sql": GOOD_SQL,
            "result_preview": "order_id\n1",
            "llm_budget": {"max_calls": 8, "used": 0},
            "messages": [],
        },
        deps,
    )
    second = str(llm.last_messages[0].content)

    assert "Punchy persona instructions." in first
    assert "Updated punchy persona instructions." in second


def test_analysis_turn_uses_saved_preference_in_prompt(settings):
    llm = ScriptLLM([f"```sql\n{GOOD_SQL}\n```", "Done"])
    capturing = CapturingLLM("Final report")
    bq = FakeBQRunner(
        [QueryResult(ok=True, dataframe=pd.DataFrame({"order_id": [1]}), sql=GOOD_SQL)]
    )
    store = ReportStore(db_path=settings.reports_db_path)
    store.set_output_format("alice", "bullets")
    deps = AgentDeps(settings=settings, llm=llm, bq_runner=bq, report_store=store)
    graph = compile_graph(deps)

    graph.invoke(
        {
            "messages": [HumanMessage(content="Show recent orders")],
            "user_id": "alice",
            "question": "Show recent orders",
        },
        _thread_config("analysis-pref"),
    )

    deps_with_capture = AgentDeps(
        settings=settings,
        llm=capturing,
        bq_runner=bq,
        report_store=store,
    )
    compose_report(
        {
            "user_id": "alice",
            "question": "Show recent orders",
            "sql": GOOD_SQL,
            "result_preview": "order_id\n1",
            "llm_budget": {"max_calls": 8, "used": 2},
            "messages": [],
        },
        deps_with_capture,
    )

    system_text = str(capturing.last_messages[0].content)
    assert "bullet points" in system_text.lower()
