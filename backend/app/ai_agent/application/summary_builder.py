from __future__ import annotations

from ..domain.analytics_dsl import AnalyticsDSL


def build_summary(dsl: AnalyticsDSL, data: list[dict[str, object]]) -> str:
    if not data:
        return "Данные не найдены по заданным фильтрам."
    metric_alias = dsl.metrics[0].as_ if dsl.metrics else "tickets"
    first = data[0]
    top_metric = first.get(metric_alias)
    dims = ", ".join(dsl.dimensions) if dsl.dimensions else "без группировки"
    return (
        f"Найдено {len(data)} строк агрегированных данных. "
        f"Основная группировка: {dims}. "
        f"Первый результат: {metric_alias}={top_metric}."
    )
