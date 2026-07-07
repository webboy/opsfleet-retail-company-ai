"""Property-based assertions for eval cases."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from retail_agent.state import AgentState


@dataclass
class AssertionResult:
    passed: bool
    failures: list[str] = field(default_factory=list)


def tables_in_sql(sql: str | None) -> set[str]:
    if not sql:
        return set()
    return {match.group(1).lower() for match in re.finditer(r"thelook_ecommerce\.(\w+)", sql, re.I)}


def evaluate_expectations(
    state: AgentState,
    expect: dict,
    *,
    bq_calls: int = 0,
    llm_calls: int = 0,
    interrupted: bool = False,
) -> AssertionResult:
    failures: list[str] = []

    if "status" in expect and state.get("status") != expect["status"]:
        failures.append(f"status expected {expect['status']!r}, got {state.get('status')!r}")

    if "guard_decision" in expect and state.get("guard_decision") != expect["guard_decision"]:
        failures.append(
            f"guard_decision expected {expect['guard_decision']!r}, got {state.get('guard_decision')!r}"
        )

    if "guard_route" in expect and state.get("guard_route") != expect["guard_route"]:
        failures.append(f"guard_route expected {expect['guard_route']!r}, got {state.get('guard_route')!r}")

    if expect.get("query_ok") is True and not state.get("query_ok"):
        failures.append("expected query_ok=True")

    if expect.get("query_empty") is False and state.get("query_empty"):
        failures.append("expected non-empty query result")

    if "sql_tables" in expect:
        found = tables_in_sql(state.get("sql"))
        missing = [table for table in expect["sql_tables"] if table not in found]
        if missing:
            failures.append(f"sql missing tables {missing}; found {sorted(found)}")

    report = (state.get("report") or "").lower()
    for token in expect.get("report_must_contain", []):
        if token.lower() not in report:
            failures.append(f"report missing required text {token!r}")

    for token in expect.get("report_must_not_contain", []):
        if token.lower() in report:
            failures.append(f"report contained forbidden text {token!r}")

    if "max_bq_calls" in expect and bq_calls > expect["max_bq_calls"]:
        failures.append(f"bq_calls={bq_calls} exceeded max {expect['max_bq_calls']}")

    if "max_llm_calls" in expect and llm_calls > expect["max_llm_calls"]:
        failures.append(f"llm_calls={llm_calls} exceeded max {expect['max_llm_calls']}")

    if expect.get("interrupt") is True and not interrupted:
        failures.append("expected graph interrupt but none occurred")
    if expect.get("interrupt") is False and interrupted:
        failures.append("unexpected graph interrupt")

    if expect.get("pii_masked") is True and not state.get("pii_masked"):
        failures.append("expected pii_masked=True")

    return AssertionResult(passed=not failures, failures=failures)
