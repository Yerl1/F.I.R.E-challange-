from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException

from ...db import _engine
from ..application.analytics_agent_service import AnalyticsAgentService
from ..application.config import get_agent_settings
from ..application.errors import AnalyticsError
from .schemas import AnalyticsQueryRequest

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

_service = AnalyticsAgentService(settings=get_agent_settings(), engine=_engine)


@router.post("/query")
def analytics_query(req: AnalyticsQueryRequest) -> dict:
    request_id = str(uuid4())
    try:
        result = _service.run(req.query, request_id=request_id)
        return result.model_dump(by_alias=True)
    except AnalyticsError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "request_id": request_id,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "hint": exc.hint,
                },
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "request_id": request_id,
                "error": {
                    "code": "internal_error",
                    "message": str(exc),
                    "hint": "Check backend logs for request details.",
                },
            },
        ) from exc
