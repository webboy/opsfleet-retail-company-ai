"""Tests for eval judge parsing."""

from __future__ import annotations

from unittest.mock import patch

from langchain_core.messages import AIMessage

from retail_agent.config import Settings
from retail_agent.evals.judge import parse_judge_response, score_intent
from retail_agent.llm import CallBudget


def test_parse_judge_response_accepts_json():
    score, rationale = parse_judge_response('{"score": 4, "rationale": "Clear answer"}')
    assert score == 4
    assert rationale == "Clear answer"


def test_parse_judge_response_falls_back_to_regex():
    score, rationale = parse_judge_response("Score: {\"score\": 5, \"rationale\": \"Great\"}")
    assert score == 5


def test_score_intent_uses_dry_run_stub():
    score, rationale = score_intent(
        {"report": "Monthly revenue rose in Q4."},
        question="What was monthly revenue?",
        dry_run={"judge_score": 4, "judge_rationale": "stub"},
    )
    assert score == 4
    assert rationale == "stub"


def test_score_intent_passes_budget_to_invoke_with_retry():
    fake_llm = object()
    settings = Settings(
        gcp_project_id="eval-project",
        google_api_key="eval-key",
        model="gemini-2.5-flash",
        embedding_model="gemini-embedding-001",
        persona="default",
        provider="gemini",
        fallback_provider="openrouter",
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
        keyword_min_overlap=2,
    )

    def fake_invoke(_llm, _messages, budget):
        assert isinstance(budget, CallBudget)
        assert budget.max_calls == 2
        return AIMessage(content='{"score": 4, "rationale": "live judge"}')

    with patch("retail_agent.evals.judge.create_chat_model", return_value=fake_llm) as create_model:
        with patch("retail_agent.evals.judge.invoke_with_retry", side_effect=fake_invoke):
            score, rationale = score_intent(
                {"report": "Revenue grew 12%."},
                question="How is revenue trending?",
                settings=settings,
            )

    create_model.assert_called_once()
    judge_settings = create_model.call_args.args[0]
    assert judge_settings.provider == "ollama"
    assert judge_settings.fallback_provider is None
    assert judge_settings.ollama_model == "llama3.2"
    assert score == 4
    assert rationale == "live judge"


def test_score_intent_returns_none_when_judge_call_fails():
    with patch("retail_agent.evals.judge.create_chat_model", return_value=object()):
        with patch(
            "retail_agent.evals.judge.invoke_with_retry",
            side_effect=RuntimeError("quota exhausted"),
        ):
            score, rationale = score_intent(
                {"report": "Revenue grew 12%."},
                question="How is revenue trending?",
            )

    assert score is None
    assert "judge unavailable" in rationale
