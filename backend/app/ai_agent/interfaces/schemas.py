from __future__ import annotations

from pydantic import BaseModel


class AnalyticsQueryRequest(BaseModel):
    query: str


class AnalyticsErrorResponse(BaseModel):
    request_id: str
    error: dict[str, str]
