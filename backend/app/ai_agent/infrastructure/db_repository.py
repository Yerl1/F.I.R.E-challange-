from __future__ import annotations

import concurrent.futures
from collections.abc import Mapping
from typing import Any

from sqlalchemy import text

from ...db import get_session
from ..application.errors import AnalyticsError


class DbRepository:
    def execute_select(
        self,
        sql: str,
        params: Mapping[str, object],
        timeout_s: float,
    ) -> list[dict[str, Any]]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self._execute_sync, sql, dict(params))
            try:
                return future.result(timeout=timeout_s)
            except concurrent.futures.TimeoutError as exc:
                raise AnalyticsError(
                    "sql_timeout",
                    "Analytics query timed out",
                    hint="Reduce date range or remove extra dimensions",
                ) from exc

    @staticmethod
    def _execute_sync(sql: str, params: dict[str, object]) -> list[dict[str, Any]]:
        with get_session() as session:
            rows = session.execute(text(sql), params).mappings().all()
            return [dict(row) for row in rows]
