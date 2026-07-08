"""Generate SQL from natural language."""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from retail_agent.deps import AgentDeps
from retail_agent.llm import (
    BudgetExhaustedError,
    CallBudget,
    invoke_with_retry,
    is_llm_unavailable_error,
    is_quota_exhausted_error,
    quota_exhausted_message,
)
from retail_agent.nodes.retrieve_trios import retrieved_examples_block
from retail_agent.schema_doc import load_schema_doc
from retail_agent.sql_utils import extract_sql
from retail_agent.state import AgentState


def generate_sql(state: AgentState, deps: AgentDeps) -> dict:
    budget = CallBudget.from_dict(state.get("llm_budget"))
    question = state.get("question") or ""
    attempts = state.get("sql_attempts", 0) + 1
    previous_sql = state.get("sql")
    last_error = state.get("last_error")

    retry_context = ""
    if attempts > 1 and previous_sql:
        retry_context = (
            f"\nPrevious SQL:\n{previous_sql}\n\n"
            f"Error or issue:\n{last_error or 'empty result set'}\n"
            "Generate a corrected SELECT query."
        )

    conversation = _conversation_snippet(state)
    examples = retrieved_examples_block(state)

    try:
        response = invoke_with_retry(
            deps.llm,
            [
                SystemMessage(
                    content=(
                        "You write BigQuery SQL for a retail analytics assistant. "
                        "Return ONLY one SELECT statement for BigQuery, wrapped in a ```sql``` "
                        "code block. Use fully qualified table names under "
                        "`bigquery-public-data.thelook_ecommerce`. "
                        "Do not use DML/DDL. Prefer clear joins and filters."
                    )
                ),
                HumanMessage(
                    content=(
                        f"Schema:\n{load_schema_doc()}\n\n"
                        f"Similar historical examples:\n{examples}\n\n"
                        f"Conversation:\n{conversation}\n\n"
                        f"Current question: {question}"
                        f"{retry_context}"
                    )
                ),
            ],
            budget,
        )
        sql = extract_sql(str(response.content))
    except BudgetExhaustedError:
        return {
            "sql_attempts": attempts,
            "status": "fallback",
            "last_error": "LLM call budget exhausted",
            "llm_budget": budget.to_dict(),
        }
    except Exception as exc:
        if is_llm_unavailable_error(exc):
            return _llm_unavailable_update(deps, budget, attempts, exc)
        raise

    return {
        "sql": sql,
        "sql_attempts": attempts,
        "llm_budget": budget.to_dict(),
        "messages": [AIMessage(content=f"Generated SQL (attempt {attempts}).")],
    }


def _conversation_snippet(state: AgentState, *, limit: int = 6) -> str:
    messages = state.get("messages") or []
    lines: list[str] = []
    for message in messages[-limit:]:
        role = getattr(message, "type", "message")
        lines.append(f"{role}: {message.content}")
    return "\n".join(lines) if lines else "(no prior conversation)"


def _llm_unavailable_update(deps: AgentDeps, budget: CallBudget, attempts: int, exc: Exception) -> dict:
    if is_quota_exhausted_error(exc):
        message = quota_exhausted_message(
            model=deps.settings.model,
            provider=deps.settings.provider,
            fallback_provider=deps.settings.fallback_provider,
        )
    else:
        message = str(exc) or "LLM authentication failed."
    return {
        "sql_attempts": attempts,
        "status": "fallback",
        "last_error": message,
        "llm_budget": budget.to_dict(),
    }
