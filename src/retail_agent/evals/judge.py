"""LLM-as-judge helpers for eval intent scoring."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import replace

from langchain_core.messages import HumanMessage, SystemMessage

from retail_agent.config import Settings
from retail_agent.evals.cases import judge_prompt_path
from retail_agent.llm import CallBudget, create_chat_model, invoke_with_retry
from retail_agent.state import AgentState

logger = logging.getLogger(__name__)

_SCORE_RE = re.compile(r'"score"\s*:\s*([1-5])', re.I)


def load_judge_prompt() -> str:
    return judge_prompt_path().read_text(encoding="utf-8").strip()


def build_judge_input(state: AgentState, *, question: str) -> str:
    return (
        f"User question:\n{question}\n\n"
        f"Generated SQL:\n{state.get('sql') or '(none)'}\n\n"
        f"Result sample:\n{state.get('result_preview') or '(none)'}\n\n"
        f"Final report:\n{state.get('report') or '(none)'}"
    )


def parse_judge_response(text: str) -> tuple[int | None, str]:
    text = text.strip()
    try:
        payload = json.loads(text)
        score = int(payload.get("score"))
        rationale = str(payload.get("rationale") or "")
        if 1 <= score <= 5:
            return score, rationale
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    match = _SCORE_RE.search(text)
    if match:
        return int(match.group(1)), text
    return None, text


def _judge_settings(settings: Settings) -> Settings:
    """Eval judge always uses local Ollama — avoids cloud quota on live eval runs."""

    return replace(
        settings,
        provider="ollama",
        fallback_provider=None,
    )


def score_intent(
    state: AgentState,
    *,
    question: str,
    settings: Settings | None = None,
    llm=None,
    dry_run: dict | None = None,
) -> tuple[int | None, str]:
    if dry_run and "judge_score" in dry_run:
        return int(dry_run["judge_score"]), str(dry_run.get("judge_rationale") or "dry-run judge")

    settings = settings or Settings(
        gcp_project_id="eval-project",
        google_api_key="eval-key",
        model="gemini-2.5-flash",
        embedding_model="gemini-embedding-001",
        persona="default",
        provider="gemini",
        fallback_provider=None,
        openrouter_api_key=None,
        openrouter_model="google/gemini-2.0-flash-exp:free",
        ollama_host="http://localhost:11434",
        ollama_model="llama3.2",
        dataset_id="bigquery-public-data.thelook_ecommerce",
        reports_db_path=None,
        personas_dir=None,
        max_bytes_billed=1_073_741_824,
        default_limit=1000,
        mcp_max_response_rows=100,
        embedding_min_similarity=0.35,
    )
    judge_settings = _judge_settings(settings)
    llm = llm or create_chat_model(judge_settings)
    messages = [
        SystemMessage(content=load_judge_prompt()),
        HumanMessage(content=build_judge_input(state, question=question)),
    ]
    try:
        response = invoke_with_retry(llm, messages, CallBudget(max_calls=2))
    except Exception as exc:  # noqa: BLE001 — judge failure must not abort the eval run
        logger.warning("Intent judge unavailable for question=%r: %s", question, exc)
        return None, f"judge unavailable: {type(exc).__name__}: {exc}"
    return parse_judge_response(getattr(response, "content", str(response)))
