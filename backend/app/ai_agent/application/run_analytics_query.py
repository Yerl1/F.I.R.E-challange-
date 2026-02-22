from __future__ import annotations

import logging
from uuid import uuid4

from sqlalchemy.engine import Engine

from ..domain.analytics_dsl import AnalyticsDSL
from ..domain.chart_result import AnalyticsResult
from ..infrastructure.db_repository import DbRepository
from ..infrastructure.sql_compiler import SqlCompiler
from ..infrastructure.sql_safety import validate_sql_is_safe
from .chart_builder import build_vega_lite_spec
from .summary_builder import build_summary

logger = logging.getLogger(__name__)


class RunAnalyticsQueryUseCase:
    def __init__(
        self,
        engine: Engine,
        repository: DbRepository,
        default_days_range: int,
        max_rows: int,
        sql_timeout_seconds: float,
    ) -> None:
        self._compiler = SqlCompiler(engine=engine, default_days_range=default_days_range, max_rows=max_rows)
        self._repository = repository
        self._sql_timeout_seconds = sql_timeout_seconds

    def execute(self, dsl: AnalyticsDSL, request_id: str | None = None) -> AnalyticsResult:
        req_id = request_id or str(uuid4())
        compiled = self._compiler.compile(dsl)
        validate_sql_is_safe(compiled.sql)
        logger.info("ai_agent request_id=%s sql=%s", req_id, compiled.sql)
        rows = self._repository.execute_select(
            sql=compiled.sql,
            params=compiled.params,
            timeout_s=self._sql_timeout_seconds,
        )
        chart_spec = build_vega_lite_spec(dsl, rows)
        summary = build_summary(dsl, rows)
        return AnalyticsResult(
            request_id=req_id,
            dsl=dsl,
            sql=compiled.sql,
            data=rows,
            chart_spec=chart_spec,
            summary=summary,
        )
