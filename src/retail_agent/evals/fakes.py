"""Deterministic fakes for dry-run eval execution."""

from __future__ import annotations

import pandas as pd
from langchain_core.messages import AIMessage

from retail_agent.bq import QueryResult


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


def query_result_from_spec(spec: dict) -> QueryResult:
    if not spec.get("ok", True):
        return QueryResult(ok=False, error=spec.get("error", "query failed"), sql=spec.get("sql", ""))
    columns = spec.get("columns") or ["value"]
    if "rows" in spec:
        rows = spec["rows"]
    else:
        rows = [[1]]
    dataframe = pd.DataFrame(rows, columns=columns)
    return QueryResult(
        ok=True,
        dataframe=dataframe,
        sql=spec.get("sql", ""),
        empty=dataframe.empty,
    )
