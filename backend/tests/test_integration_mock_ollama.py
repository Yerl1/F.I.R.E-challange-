from unittest.mock import patch

from sqlalchemy import create_engine

from backend.app.ai_agent.application.config import AgentSettings
from backend.app.ai_agent.application.interpret_query import InterpretQueryUseCase
from backend.app.ai_agent.application.run_analytics_query import RunAnalyticsQueryUseCase
from backend.app.ai_agent.infrastructure.db_repository import DbRepository
from backend.app.ai_agent.infrastructure.ollama_client import OllamaClient


class FakeDbRepository(DbRepository):
    def execute_select(self, sql: str, params: dict[str, object], timeout_s: float):  # type: ignore[override]
        return [{"city": "Astana", "tickets": 10}, {"city": "Almaty", "tickets": 8}]


def test_mocked_ollama_to_result() -> None:
    settings = AgentSettings(
        ollama_base_url="http://ollama:11434",
        ollama_model="qwen2.5:7b-instruct-q4_K_M",
        default_days_range=30,
        max_rows=500,
        sql_timeout_seconds=5.0,
        ollama_timeout_seconds=5.0,
    )
    client = OllamaClient(settings.ollama_base_url, settings.ollama_model, timeout_s=5.0)
    with patch.object(
        OllamaClient,
        "generate_dsl_json",
        return_value={
            "intent": "distribution",
            "metrics": [{"name": "count", "field": "*", "as": "tickets"}],
            "dimensions": ["city"],
            "filters": [],
            "time_grain": "null",
            "limit": 100,
            "chart": {"type": "bar", "x": "city", "y": "tickets"},
        },
    ):
        dsl = InterpretQueryUseCase(client=client, default_days_range=30, max_rows=500).execute(
            "Покажи распределение обращений по городам"
        )
    runner = RunAnalyticsQueryUseCase(
        engine=create_engine("sqlite:///:memory:"),
        repository=FakeDbRepository(),
        default_days_range=30,
        max_rows=500,
        sql_timeout_seconds=5.0,
    )
    result = runner.execute(dsl=dsl, request_id="req-1")
    assert result.request_id == "req-1"
    assert len(result.data) == 2
    assert "mark" in result.chart_spec
