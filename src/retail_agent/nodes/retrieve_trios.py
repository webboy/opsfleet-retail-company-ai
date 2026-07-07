"""Retrieve relevant Golden Bucket trios for the current question."""

from __future__ import annotations

import logging

from retail_agent.deps import AgentDeps
from retail_agent.golden import format_trios_for_prompt
from retail_agent.state import AgentState

logger = logging.getLogger(__name__)


def retrieve_trios(state: AgentState, deps: AgentDeps) -> dict:
    question = state.get("question") or ""
    result = deps.trio_store.retrieve(question)
    trio_dicts = [trio.to_dict() for trio in result.trios]
    logger.info(
        "Retrieved trios ids=%s method=%s",
        [trio.id for trio in result.trios],
        result.method,
    )
    return {
        "retrieved_trios": trio_dicts,
        "retrieved_trio_ids": [trio.id for trio in result.trios],
        "retrieval_method": result.method,
    }


def retrieved_examples_block(state: AgentState) -> str:
    from retail_agent.golden import trios_from_state

    return format_trios_for_prompt(trios_from_state(state.get("retrieved_trios")))
