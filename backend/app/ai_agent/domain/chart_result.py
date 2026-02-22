from __future__ import annotations

from pydantic import BaseModel, Field

from .analytics_dsl import AnalyticsDSL


class AnalyticsResult(BaseModel):
    request_id: str
    dsl: AnalyticsDSL
    sql: str
    data: list[dict[str, object]] = Field(default_factory=list)
    chart_spec: dict[str, object] = Field(default_factory=dict)
    summary: str
