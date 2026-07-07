"""Runtime dependencies injected into graph nodes."""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.language_models.chat_models import BaseChatModel

from retail_agent.bq import BigQueryRunner
from retail_agent.config import Settings, get_settings
from retail_agent.golden import TrioStore
from retail_agent.llm import CallBudget, create_chat_model


@dataclass
class AgentDeps:
    settings: Settings
    llm: BaseChatModel
    bq_runner: BigQueryRunner
    trio_store: TrioStore | None = None
    max_sql_attempts: int = 3
    max_llm_calls: int = 8

    def __post_init__(self) -> None:
        if self.trio_store is None:
            self.trio_store = TrioStore(settings=self.settings)

    @classmethod
    def create(
        cls,
        settings: Settings | None = None,
        llm: BaseChatModel | None = None,
        bq_runner: BigQueryRunner | None = None,
        trio_store: TrioStore | None = None,
        *,
        max_sql_attempts: int = 3,
        max_llm_calls: int = 8,
    ) -> AgentDeps:
        settings = settings or get_settings()
        return cls(
            settings=settings,
            llm=llm or create_chat_model(settings),
            bq_runner=bq_runner or BigQueryRunner(settings=settings),
            trio_store=trio_store or TrioStore(settings=settings),
            max_sql_attempts=max_sql_attempts,
            max_llm_calls=max_llm_calls,
        )


def fresh_budget(deps: AgentDeps) -> CallBudget:
    return CallBudget(max_calls=deps.max_llm_calls)
