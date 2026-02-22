from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ..domain.analytics_dsl import AnalyticsDSL, ChartHint, FilterCondition, Metric
from ..infrastructure.ollama_client import OllamaClient


class InterpretQueryUseCase:
    def __init__(self, client: OllamaClient, default_days_range: int, max_rows: int) -> None:
        self._client = client
        self._default_days_range = default_days_range
        self._max_rows = max_rows

    def execute(self, query: str) -> AnalyticsDSL:
        prompt = self._build_prompt(query)
        raw = self._client.generate_dsl_json(prompt)
        dsl = AnalyticsDSL.model_validate(raw)
        return self._postprocess(dsl)

    def _postprocess(self, dsl: AnalyticsDSL) -> AnalyticsDSL:
        if not dsl.metrics:
            dsl.metrics = [Metric()]
        if dsl.chart is None:
            dsl.chart = ChartHint()
        if not dsl.filters:
            start_dt = datetime.now(timezone.utc) - timedelta(days=self._default_days_range)
            dsl.filters = [
                FilterCondition(field="created_at", op=">=", value=start_dt.isoformat())
            ]
        dsl.limit = max(1, min(dsl.limit, self._max_rows))
        if dsl.chart.type == "table":
            dsl.intent = "table"
        if not dsl.chart.type:
            dsl.chart.type = "line" if dsl.intent == "trend" else "bar"
        return dsl

    @staticmethod
    def _build_prompt(query: str) -> str:
        schema = """
Return ONLY JSON object with this schema:
{
  "intent": "distribution|trend|top_n|comparison|table",
  "metrics": [{"name":"count","field":"*","as":"tickets"}],
  "dimensions": ["city","ticket_type"],
  "filters": [{"field":"created_at","op":">=","value":"2026-01-01T00:00:00Z"}],
  "time_grain": "day|week|month|null",
  "limit": 100,
  "chart": {"type":"bar|stacked_bar|line|pie|heatmap|table", "x":"...", "y":"...", "series":"..."}
}

Allowed fields: created_at, city, ticket_type(type), sentiment, segment, language, priority, office_id, manager_id.
Rules:
- Use count metric unless user asks table/raw rows.
- If date range not provided, still return valid DSL without invented columns.
- No SQL, no markdown, no explanations. JSON only.
"""
        return f"{schema}\nUser request: {query}"
