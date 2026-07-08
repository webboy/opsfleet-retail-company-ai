"""Graph integration tests for saved reports and delete confirmation."""

from __future__ import annotations

import pandas as pd
import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command

from retail_agent.bq import QueryResult
from retail_agent.deps import AgentDeps
from retail_agent.graph import compile_graph
from retail_agent.stores import ReportStore
from tests.helpers import make_settings
from tests.test_graph import FakeBQRunner, ScriptLLM

GOOD_SQL = (
    "SELECT order_id FROM `bigquery-public-data.thelook_ecommerce.orders` LIMIT 5"
)


@pytest.fixture
def settings(tmp_path):
    return make_settings(google_api_key="test-key", reports_db_path=str(tmp_path / "reports.sqlite3"))


@pytest.fixture
def deps(settings):
    llm = ScriptLLM(["unused"])
    bq = FakeBQRunner([])
    report_store = ReportStore(db_path=settings.reports_db_path)
    return AgentDeps(settings=settings, llm=llm, bq_runner=bq, report_store=report_store)


def _thread_config(thread_id: str = "reports-thread"):
    return {"configurable": {"thread_id": thread_id}}


def _seed_analysis_report(deps: AgentDeps, *, thread_id: str = "reports-thread"):
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
    graph.invoke(
        {
            "messages": [HumanMessage(content="How did revenue trend?")],
            "user_id": "alice",
            "question": "How did revenue trend?",
        },
        config,
    )
    return graph, config


def test_save_current_report_after_analysis(deps):
    graph, config = _seed_analysis_report(deps)

    result = graph.invoke(
        {
            "messages": [HumanMessage(content="save this report")],
            "user_id": "alice",
            "question": "save this report",
        },
        config,
    )

    assert "Saved report" in result["report"]
    saved = deps.report_store.list_reports("alice")
    assert len(saved) == 1
    assert saved[0].content == "Revenue grew 12% in Q1."
    assert saved[0].question == "How did revenue trend?"


def test_save_after_preference_turn_keeps_analysis_report(deps):
    graph, config = _seed_analysis_report(deps, thread_id="pref-then-save")

    graph.invoke(
        {
            "messages": [HumanMessage(content="I prefer bullet points from now on")],
            "user_id": "alice",
            "question": "I prefer bullet points from now on",
        },
        config,
    )

    result = graph.invoke(
        {
            "messages": [HumanMessage(content="save this report")],
            "user_id": "alice",
            "question": "save this report",
        },
        config,
    )

    assert "Saved report" in result["report"]
    saved = deps.report_store.list_reports("alice")
    assert len(saved) == 1
    assert saved[0].title == "How did revenue trend?"
    assert saved[0].content == "Revenue grew 12% in Q1."
    assert "Saved your preference" not in saved[0].content


def test_save_after_list_turn_keeps_analysis_report(deps):
    graph, config = _seed_analysis_report(deps, thread_id="list-then-save")

    graph.invoke(
        {
            "messages": [HumanMessage(content="show my reports")],
            "user_id": "alice",
            "question": "show my reports",
        },
        config,
    )

    result = graph.invoke(
        {
            "messages": [HumanMessage(content="save this report")],
            "user_id": "alice",
            "question": "save this report",
        },
        config,
    )

    assert "Saved report" in result["report"]
    saved = deps.report_store.list_reports("alice")
    assert len(saved) == 1
    assert saved[0].title == "How did revenue trend?"
    assert saved[0].content == "Revenue grew 12% in Q1."
    assert "don't have any saved reports" not in saved[0].content


def test_save_with_no_analysis_report_saves_nothing(deps):
    graph = compile_graph(deps)
    config = _thread_config("refusal-only-save")

    graph.invoke(
        {
            "messages": [HumanMessage(content="Write me a poem about the moon")],
            "user_id": "alice",
            "question": "Write me a poem about the moon",
        },
        config,
    )

    result = graph.invoke(
        {
            "messages": [HumanMessage(content="save this report")],
            "user_id": "alice",
            "question": "save this report",
        },
        config,
    )

    assert "no recent report to save" in result["report"].lower()
    assert deps.report_store.list_reports("alice") == []


def test_list_reports_returns_owner_scoped_summaries(deps):
    deps.report_store.save_report(
        owner="alice",
        title="Client X summary",
        content="Client X revenue",
    )
    deps.report_store.save_report(
        owner="bob",
        title="Bob private report",
        content="hidden",
    )

    graph = compile_graph(deps)
    result = graph.invoke(
        {
            "messages": [HumanMessage(content="show my reports")],
            "user_id": "alice",
            "question": "show my reports",
        },
        _thread_config("list-thread"),
    )

    assert "Client X summary" in result["report"]
    assert "Bob private report" not in result["report"]


def test_delete_by_mention_interrupt_confirm_deletes(deps):
    deps.report_store.save_report(
        owner="alice",
        title="Client X summary",
        content="Client X revenue",
    )

    graph = compile_graph(deps)
    config = _thread_config("delete-confirm")

    graph.invoke(
        {
            "messages": [HumanMessage(content="delete reports mentioning Client X")],
            "user_id": "alice",
            "question": "delete reports mentioning Client X",
        },
        config,
    )
    snapshot = graph.get_state(config)
    assert snapshot.next

    result = graph.invoke(Command(resume="yes"), config)
    assert "Deleted 1" in result["report"]
    assert deps.report_store.list_reports("alice") == []


def test_delete_interrupt_decline_keeps_reports(deps):
    deps.report_store.save_report(
        owner="alice",
        title="Client X summary",
        content="Client X revenue",
    )

    graph = compile_graph(deps)
    config = _thread_config("delete-decline")

    graph.invoke(
        {
            "messages": [HumanMessage(content="delete reports mentioning Client X")],
            "user_id": "alice",
            "question": "delete reports mentioning Client X",
        },
        config,
    )
    assert graph.get_state(config).next

    result = graph.invoke(Command(resume="no"), config)
    assert "cancelled" in result["report"].lower()
    assert len(deps.report_store.list_reports("alice")) == 1


def test_delete_interrupt_gibberish_cancels(deps):
    deps.report_store.save_report(
        owner="alice",
        title="Client X summary",
        content="Client X revenue",
    )

    graph = compile_graph(deps)
    config = _thread_config("delete-gibberish")

    graph.invoke(
        {
            "messages": [HumanMessage(content="delete reports mentioning Client X")],
            "user_id": "alice",
            "question": "delete reports mentioning Client X",
        },
        config,
    )

    result = graph.invoke(Command(resume="banana"), config)
    assert "cancelled" in result["report"].lower()
    assert len(deps.report_store.list_reports("alice")) == 1


def test_bob_cannot_delete_alice_reports(deps):
    deps.report_store.save_report(
        owner="alice",
        title="Client X summary",
        content="Client X revenue",
    )

    graph = compile_graph(deps)
    result = graph.invoke(
        {
            "messages": [HumanMessage(content="delete reports mentioning Client X")],
            "user_id": "bob",
            "question": "delete reports mentioning Client X",
        },
        _thread_config("bob-delete"),
    )

    assert "couldn't find" in result["report"].lower()
    assert len(deps.report_store.list_reports("alice")) == 1
