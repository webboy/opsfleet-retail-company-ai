"""Graph integration tests for Golden Bucket retrieval and capture."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from langchain_core.messages import AIMessage, HumanMessage

from retail_agent.bq import QueryResult
from retail_agent.deps import AgentDeps
from retail_agent.golden import FakeEmbedder, TrioStore
from retail_agent.graph import compile_graph
from retail_agent.nodes.generate_sql import generate_sql
from retail_agent.nodes.retrieve_trios import retrieve_trios
from tests.helpers import make_settings
from tests.test_graph import GOOD_SQL, FakeBQRunner, ScriptLLM


SAMPLE_TRIO = """\
---
id: top-customers-spend
question: Who are our top 10 customers by total spend?
tags:
  - customers
  - revenue
sql: |
  SELECT user_id, SUM(sale_price) AS total_spend
  FROM `bigquery-public-data.thelook_ecommerce.order_items`
  GROUP BY user_id
  LIMIT 10
report: |
  Rank customers by completed order spend.
---
"""


class RecordingLLM:
    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.calls = 0
        self.last_messages = None

    def invoke(self, messages):
        self.last_messages = messages
        content = self._responses[min(self.calls, len(self._responses) - 1)]
        self.calls += 1
        return AIMessage(content=content)


@pytest.fixture
def bucket_dir(tmp_path: Path) -> Path:
    (tmp_path / "top-customers-spend.md").write_text(SAMPLE_TRIO, encoding="utf-8")
    return tmp_path


def _trio_store(bucket_dir: Path) -> TrioStore:
    return TrioStore(
        bucket_dir,
        embedder=FakeEmbedder(),
        settings=make_settings(),
        embedding_enabled=True,
        top_k=2,
    )


def _deps(bucket_dir: Path, llm, bq) -> AgentDeps:
    return AgentDeps(
        settings=make_settings(),
        llm=llm,
        bq_runner=bq,
        trio_store=_trio_store(bucket_dir),
    )


def test_retrieve_trios_runs_before_sql_generation(bucket_dir: Path):
    deps = _deps(bucket_dir, ScriptLLM(["unused"]), FakeBQRunner([]))
    state = {"question": "Who are our top customers by total spend?"}

    update = retrieve_trios(state, deps)

    assert update["retrieval_method"] == "embedding"
    assert update["retrieved_trio_ids"] == ["top-customers-spend"]
    assert "top 10 customers" in update["retrieved_trios"][0]["question"].lower()


def test_generate_sql_prompt_includes_retrieved_examples(bucket_dir: Path):
    deps = _deps(bucket_dir, RecordingLLM([f"```sql\n{GOOD_SQL}\n```"]), FakeBQRunner([]))
    state = {
        "question": "Who are our top customers by total spend?",
        "retrieved_trios": retrieve_trios(
            {"question": "Who are our top customers by total spend?"},
            deps,
        )["retrieved_trios"],
    }

    generate_sql(state, deps)

    human_content = str(deps.llm.last_messages[1].content)
    assert "Similar historical examples" in human_content
    assert "top 10 customers" in human_content.lower()
    assert "SELECT user_id" in human_content


def test_successful_graph_turn_captures_candidate(bucket_dir: Path):
    llm = ScriptLLM([f"```sql\n{GOOD_SQL}\n```", "Top customers report"])
    bq = FakeBQRunner(
        [QueryResult(ok=True, dataframe=pd.DataFrame({"order_id": [1]}), sql=GOOD_SQL)]
    )
    deps = _deps(bucket_dir, llm, bq)
    graph = compile_graph(deps)

    result = graph.invoke(
        {
            "messages": [HumanMessage(content="Who are our top customers by total spend?")],
            "user_id": "alice",
            "question": "Who are our top customers by total spend?",
        },
        {"configurable": {"thread_id": "golden-capture-thread"}},
    )

    assert result["status"] == "done"
    assert result.get("candidate_captured") is True
    assert result["retrieved_trio_ids"] == ["top-customers-spend"]

    candidate_path = bucket_dir / "candidates" / "candidates.jsonl"
    assert candidate_path.exists()
    record = json.loads(candidate_path.read_text(encoding="utf-8").strip())
    assert record["question"] == "Who are our top customers by total spend?"
    assert record["report"] == "Top customers report"
    assert record["retrieved_trio_ids"] == ["top-customers-spend"]
