from __future__ import annotations

from uuid import uuid4

from sqlalchemy.engine import Engine

from ..domain.chart_result import AnalyticsResult
from ..infrastructure.db_repository import DbRepository
from ..infrastructure.ollama_client import OllamaClient
from .config import AgentSettings
from .interpret_query import InterpretQueryUseCase
from .run_analytics_query import RunAnalyticsQueryUseCase


class AnalyticsAgentService:
    def __init__(self, settings: AgentSettings, engine: Engine) -> None:
        self._settings = settings
        self._interpret = InterpretQueryUseCase(
            client=OllamaClient(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
                timeout_s=settings.ollama_timeout_seconds,
            ),
            default_days_range=settings.default_days_range,
            max_rows=settings.max_rows,
        )
        self._runner = RunAnalyticsQueryUseCase(
            engine=engine,
            repository=DbRepository(),
            default_days_range=settings.default_days_range,
            max_rows=settings.max_rows,
            sql_timeout_seconds=settings.sql_timeout_seconds,
        )

    def run(self, query_text: str, request_id: str | None = None) -> AnalyticsResult:
        request_id = request_id or str(uuid4())
        dsl = self._interpret.execute(query_text)
        return self._runner.execute(dsl=dsl, request_id=request_id)
