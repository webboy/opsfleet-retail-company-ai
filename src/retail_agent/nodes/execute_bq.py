"""Execute guarded SQL against BigQuery."""

from __future__ import annotations

from retail_agent.deps import AgentDeps
from retail_agent.state import AgentState


def execute_bq(state: AgentState, deps: AgentDeps) -> dict:
    sql = state.get("sql") or ""
    result = deps.bq_runner.execute(sql)

    if not result.ok:
        return {
            "query_ok": False,
            "query_empty": False,
            "last_error": result.error or "Query failed",
            "result_preview": None,
        }

    if result.empty:
        return {
            "query_ok": True,
            "query_empty": True,
            "last_error": None,
            "result_preview": "(empty result set)",
        }

    assert result.dataframe is not None
    return {
        "query_ok": True,
        "query_empty": False,
        "last_error": None,
        "result_rows": result.dataframe.to_dict(orient="records"),
        "result_preview": None,
    }
