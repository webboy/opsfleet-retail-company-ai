"""Graph integration tests with mocked LLM and BigQuery."""

from __future__ import annotations

import pandas as pd
import pytest
from langchain_core.messages import AIMessage, HumanMessage

from retail_agent.bq import QueryResult
from retail_agent.deps import AgentDeps
from retail_agent.graph import compile_graph
from retail_agent.llm import CallBudget
from tests.helpers import make_settings

GOOD_SQL = (
    "SELECT order_id FROM `bigquery-public-data.thelook_ecommerce.orders` LIMIT 5"
)
BAD_SQL = "SELECT bad_column FROM `bigquery-public-data.thelook_ecommerce.orders` LIMIT 5"


class ScriptLLM:
    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.calls = 0

    def invoke(self, messages):
        content = self._responses[min(self.calls, len(self._responses) - 1)]
        self.calls += 1
        return AIMessage(content=content)


class FakeBQRunner:
    def __init__(self, outcomes: list[QueryResult]):
        self._outcomes = list(outcomes)
        self.calls = 0
        self.queries: list[str] = []

    def execute(self, sql: str) -> QueryResult:
        self.queries.append(sql)
        outcome = self._outcomes[min(self.calls, len(self._outcomes) - 1)]
        self.calls += 1
        return outcome


@pytest.fixture
def settings():
    return make_settings(google_api_key="test-key")


def _run_turn(deps: AgentDeps, question: str, *, prior: list | None = None):
    graph = compile_graph(deps)
    messages = list(prior or [])
    messages.append(HumanMessage(content=question))
    return graph.invoke(
        {"messages": messages, "user_id": "alice", "question": question},
        {"configurable": {"thread_id": "test-thread"}},
    )


def test_happy_path_generates_sql_runs_bq_and_composes_report(settings):
    llm = ScriptLLM([f"```sql\n{GOOD_SQL}\n```", "Top orders report"])
    bq = FakeBQRunner(
        [QueryResult(ok=True, dataframe=pd.DataFrame({"order_id": [1, 2]}), sql=GOOD_SQL)]
    )
    deps = AgentDeps(settings=settings, llm=llm, bq_runner=bq)

    result = _run_turn(deps, "Show me recent orders")

    assert result["status"] == "done"
    assert "Top orders report" in result["report"]
    assert bq.calls == 1
    assert llm.calls == 2


def test_self_heal_retries_after_query_error(settings):
    llm = ScriptLLM(
        [
            f"```sql\n{BAD_SQL}\n```",
            f"```sql\n{GOOD_SQL}\n```",
            "Recovered report",
        ]
    )
    bq = FakeBQRunner(
        [
            QueryResult(ok=False, error="Unrecognized name: bad_column", sql=BAD_SQL),
            QueryResult(ok=True, dataframe=pd.DataFrame({"order_id": [3]}), sql=GOOD_SQL),
        ]
    )
    deps = AgentDeps(settings=settings, llm=llm, bq_runner=bq, max_sql_attempts=3)

    result = _run_turn(deps, "Show me recent orders")

    assert result["status"] == "done"
    assert result["report"] == "Recovered report"
    assert bq.calls == 2
    assert llm.calls == 3


def test_self_heal_exhaustion_returns_fallback(settings):
    llm = ScriptLLM([f"```sql\n{BAD_SQL}\n```"] * 3)
    bq = FakeBQRunner(
        [QueryResult(ok=False, error="Unrecognized name: bad_column", sql=BAD_SQL)] * 3
    )
    deps = AgentDeps(settings=settings, llm=llm, bq_runner=bq, max_sql_attempts=3)

    result = _run_turn(deps, "Show me recent orders")

    assert result["status"] == "fallback"
    assert "couldn't answer" in result["report"].lower()
    assert bq.calls == 3


def test_schema_question_routes_to_schema_answer(settings):
    llm = ScriptLLM(["We have orders, order_items, products, and users tables."])
    bq = FakeBQRunner([])
    deps = AgentDeps(settings=settings, llm=llm, bq_runner=bq)

    result = _run_turn(deps, "What tables and columns do you have?")

    assert result["status"] == "done"
    assert "orders" in result["report"].lower()
    assert bq.calls == 0
    assert llm.calls == 1


def test_greeting_routes_without_llm_or_bq(settings):
    llm = ScriptLLM(["should not be called"])
    bq = FakeBQRunner([])
    deps = AgentDeps(settings=settings, llm=llm, bq_runner=bq)

    result = _run_turn(deps, "Helo")

    assert result["status"] == "done"
    assert "retail data analysis assistant" in result["report"].lower()
    assert bq.calls == 0
    assert llm.calls == 0


def test_invalid_sql_prose_self_heals_without_crashing(settings):
    prose = "a you'd like to retrieve from the BigQuery tables"
    llm = ScriptLLM(
        [
            prose,
            f"```sql\n{GOOD_SQL}\n```",
            "Recovered after invalid sql",
        ]
    )
    bq = FakeBQRunner(
        [
            QueryResult(ok=False, error="SQL parse error: invalid syntax", sql=prose),
            QueryResult(ok=True, dataframe=pd.DataFrame({"order_id": [1]}), sql=GOOD_SQL),
        ]
    )
    deps = AgentDeps(settings=settings, llm=llm, bq_runner=bq, max_sql_attempts=3)

    result = _run_turn(deps, "Show me something")

    assert result["status"] == "done"
    assert bq.calls == 2
    assert llm.calls == 3


def test_budget_exhaustion_returns_controlled_fallback(settings):
    llm = ScriptLLM(["unused"])
    bq = FakeBQRunner([])
    deps = AgentDeps(settings=settings, llm=llm, bq_runner=bq, max_llm_calls=0)

    result = _run_turn(deps, "Show me recent orders")

    assert result["status"] == "fallback"
    assert "budget" in (result.get("last_error") or result["report"]).lower()


def test_follow_up_question_keeps_conversation_context(settings):
    llm = ScriptLLM(
        [
            f"```sql\n{GOOD_SQL}\n```",
            "First answer",
            f"```sql\n{GOOD_SQL}\n```",
            "Follow-up answer",
        ]
    )
    bq = FakeBQRunner(
        [
            QueryResult(ok=True, dataframe=pd.DataFrame({"order_id": [1]}), sql=GOOD_SQL),
            QueryResult(ok=True, dataframe=pd.DataFrame({"order_id": [2]}), sql=GOOD_SQL),
        ]
    )
    deps = AgentDeps(settings=settings, llm=llm, bq_runner=bq)
    graph = compile_graph(deps)
    config = {"configurable": {"thread_id": "follow-up-thread"}}

    first = graph.invoke(
        {"messages": [HumanMessage(content="Show orders")], "user_id": "alice", "question": "Show orders"},
        config,
    )
    second = graph.invoke(
        {
            "messages": [HumanMessage(content="and how about last month?")],
            "user_id": "alice",
            "question": "and how about last month?",
        },
        config,
    )

    assert first["report"] == "First answer"
    assert second["report"] == "Follow-up answer"
    assert llm.calls == 4
