from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.engine import Engine

from ..application.errors import AnalyticsError
from ..domain.analytics_dsl import AnalyticsDSL, FilterCondition


@dataclass(frozen=True)
class CompiledQuery:
    sql: str
    params: dict[str, object]


class SqlCompiler:
    def __init__(self, engine: Engine, default_days_range: int, max_rows: int) -> None:
        self._engine = engine
        self._default_days_range = default_days_range
        self._max_rows = max_rows
        self._field_map = _build_field_map(engine)

    def compile(self, dsl: AnalyticsDSL) -> CompiledQuery:
        dimensions = dsl.dimensions or []
        metric_alias = dsl.metrics[0].as_ if dsl.metrics else "tickets"
        metric_sql = f"COUNT(*) AS {metric_alias}"

        select_parts: list[str] = []
        group_by_parts: list[str] = []
        order_parts: list[str] = []
        params: dict[str, object] = {}

        for idx, dim in enumerate(dimensions):
            expr = self._resolve_dimension(dim, dsl.time_grain)
            alias = _safe_alias(dim)
            select_parts.append(f"{expr} AS {alias}")
            group_by_parts.append(expr)
            order_parts.append(alias)
            if idx > 3:
                raise AnalyticsError("dsl_too_many_dimensions", "Too many dimensions requested", hint="Use up to 4")

        if dsl.intent in {"distribution", "trend", "top_n", "comparison"}:
            if not select_parts:
                default_dim = "created_at" if dsl.intent == "trend" else "ticket_type"
                expr = self._resolve_dimension(default_dim, dsl.time_grain)
                alias = _safe_alias(default_dim)
                select_parts.append(f"{expr} AS {alias}")
                group_by_parts.append(expr)
                order_parts.append(alias)
            select_clause = ", ".join([*select_parts, metric_sql])
        elif dsl.intent == "table":
            if not select_parts:
                select_parts = [
                    "external_ticket_id AS ticket_id",
                    f"{self._field_map['created_at']} AS created_at",
                    f"{self._field_map['ticket_type']} AS ticket_type",
                    f"{self._field_map['city']} AS city",
                    f"{self._field_map['priority']} AS priority",
                ]
            select_clause = ", ".join(select_parts)
        else:
            raise AnalyticsError("dsl_unknown_intent", f"Unsupported intent: {dsl.intent}")

        where_sql = self._compile_where(dsl.filters, params)
        if not any(f.field == "created_at" for f in dsl.filters):
            start_dt = datetime.now(timezone.utc) - timedelta(days=self._default_days_range)
            params["default_start_at"] = start_dt.isoformat()
            where_sql = f"{where_sql} AND {self._field_map['created_at']} >= :default_start_at"

        limit = max(1, min(dsl.limit, self._max_rows))
        params["limit"] = limit

        if dsl.intent in {"distribution", "trend", "top_n", "comparison"}:
            if not group_by_parts:
                raise AnalyticsError("dsl_group_by_required", "Aggregation requires at least one dimension")
            order_metric = metric_alias
            order_tail = "DESC" if dsl.intent in {"top_n", "distribution", "comparison"} else "ASC"
            sql = (
                f"SELECT {select_clause} "
                f"FROM ticket_results "
                f"WHERE {where_sql} "
                f"GROUP BY {', '.join(group_by_parts)} "
                f"ORDER BY {order_metric} {order_tail} "
                f"LIMIT :limit"
            )
        else:
            order_by = ", ".join(order_parts) if order_parts else "created_at DESC"
            sql = (
                f"SELECT {select_clause} "
                f"FROM ticket_results "
                f"WHERE {where_sql} "
                f"ORDER BY {order_by} "
                f"LIMIT :limit"
            )

        return CompiledQuery(sql=sql, params=params)

    def _resolve_dimension(self, field: str, time_grain: str | None) -> str:
        normalized = field.strip().lower()
        if normalized == "type":
            normalized = "ticket_type"
        if normalized in {"created_at", "date"} and time_grain and time_grain != "null":
            return self._time_bucket_sql(self._field_map["created_at"], time_grain)
        if normalized not in self._field_map:
            raise AnalyticsError("dsl_unknown_field", f"Unknown field: {field}", hint="Use allowed fields")
        return self._field_map[normalized]

    def _compile_where(self, filters: list[FilterCondition], params: dict[str, object]) -> str:
        if not filters:
            return "1=1"
        chunks: list[str] = []
        for idx, item in enumerate(filters):
            field = item.field.strip().lower()
            if field == "type":
                field = "ticket_type"
            if field not in self._field_map:
                raise AnalyticsError("dsl_unknown_filter_field", f"Unknown filter field: {item.field}")
            column_expr = self._field_map[field]
            key = f"f_{idx}"
            if item.op == "in":
                if not isinstance(item.value, list) or not item.value:
                    raise AnalyticsError("dsl_invalid_filter", "IN filter requires non-empty list")
                binds = []
                for j, val in enumerate(item.value):
                    bind_key = f"{key}_{j}"
                    params[bind_key] = val
                    binds.append(f":{bind_key}")
                chunks.append(f"{column_expr} IN ({', '.join(binds)})")
            else:
                params[key] = item.value
                chunks.append(f"{column_expr} {item.op} :{key}")
        return " AND ".join(chunks)

    def _time_bucket_sql(self, column: str, time_grain: str) -> str:
        dialect = self._engine.dialect.name
        if dialect.startswith("sqlite"):
            if time_grain == "day":
                return f"strftime('%Y-%m-%d', {column})"
            if time_grain == "week":
                return f"strftime('%Y-W%W', {column})"
            if time_grain == "month":
                return f"strftime('%Y-%m', {column})"
        else:
            if time_grain == "day":
                return f"to_char(date_trunc('day', {column}), 'YYYY-MM-DD')"
            if time_grain == "week":
                return f"to_char(date_trunc('week', {column}), 'IYYY-\"W\"IW')"
            if time_grain == "month":
                return f"to_char(date_trunc('month', {column}), 'YYYY-MM')"
        raise AnalyticsError("dsl_invalid_time_grain", f"Unsupported time_grain: {time_grain}")


def _build_field_map(engine: Engine) -> dict[str, str]:
    dialect = engine.dialect.name
    if dialect.startswith("sqlite"):
        city_expr = "COALESCE(NULLIF(json_extract(payload, '$.city'), ''), 'unknown')"
    else:
        city_expr = "COALESCE(NULLIF(payload->>'city', ''), 'unknown')"
    return {
        "created_at": "created_at",
        "city": city_expr,
        "ticket_type": "ticket_type",
        "sentiment": "sentiment",
        "segment": "segment",
        "language": "language",
        "priority": "priority",
        "office_id": "office_id",
        "manager_id": "manager_id",
    }


def _safe_alias(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum() or ch == "_") or "field"
