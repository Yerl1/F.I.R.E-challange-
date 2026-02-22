from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


Intent = Literal["distribution", "trend", "top_n", "comparison", "table"]
TimeGrain = Literal["day", "week", "month", "null"]
ChartType = Literal["bar", "stacked_bar", "line", "pie", "heatmap", "table"]
FilterOp = Literal["=", "!=", ">", ">=", "<", "<=", "in"]


class Metric(BaseModel):
    name: Literal["count"] = "count"
    field: str = "*"
    as_: str = Field(default="tickets", alias="as")


class FilterCondition(BaseModel):
    field: str
    op: FilterOp
    value: str | int | float | list[str] | list[int] | list[float]


class ChartHint(BaseModel):
    type: ChartType = "bar"
    x: str | None = None
    y: str | None = None
    series: str | None = None


class AnalyticsDSL(BaseModel):
    intent: Intent = "distribution"
    metrics: list[Metric] = Field(default_factory=lambda: [Metric()])
    dimensions: list[str] = Field(default_factory=list)
    filters: list[FilterCondition] = Field(default_factory=list)
    time_grain: TimeGrain | None = "null"
    limit: int = 100
    chart: ChartHint = Field(default_factory=ChartHint)

    @field_validator("limit")
    @classmethod
    def _validate_limit(cls, value: int) -> int:
        if value <= 0:
            return 1
        return value
