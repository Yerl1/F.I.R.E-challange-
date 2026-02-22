from __future__ import annotations

from ..domain.analytics_dsl import AnalyticsDSL


def build_vega_lite_spec(dsl: AnalyticsDSL, data: list[dict[str, object]]) -> dict[str, object]:
    chart_type = dsl.chart.type
    metric_alias = dsl.metrics[0].as_ if dsl.metrics else "tickets"
    dimensions = dsl.dimensions or []

    x = dsl.chart.x or (dimensions[0] if dimensions else metric_alias)
    y = dsl.chart.y or (metric_alias if dimensions else metric_alias)
    series = dsl.chart.series or (dimensions[1] if len(dimensions) > 1 else None)

    mark_map = {
        "bar": "bar",
        "stacked_bar": "bar",
        "line": "line",
        "pie": "arc",
        "heatmap": "rect",
        "table": "bar",
    }
    mark = mark_map.get(chart_type, "bar")

    encoding: dict[str, object] = {
        "x": {"field": x, "type": "nominal"},
        "y": {"field": y, "type": "quantitative"},
    }
    if chart_type == "line" and x:
        encoding["x"] = {"field": x, "type": "temporal"}
    if series:
        encoding["color"] = {"field": series, "type": "nominal"}
    if chart_type == "pie":
        encoding = {
            "theta": {"field": y, "type": "quantitative"},
            "color": {"field": x, "type": "nominal"},
        }
    if chart_type == "heatmap":
        y_dim = dimensions[1] if len(dimensions) > 1 else y
        encoding = {
            "x": {"field": x, "type": "nominal"},
            "y": {"field": y_dim, "type": "nominal"},
            "color": {"field": metric_alias, "type": "quantitative"},
        }

    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": "AI analytics chart",
        "data": {"values": data},
        "mark": mark,
        "encoding": encoding,
    }
