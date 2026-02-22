from __future__ import annotations

import logging

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .ai_agent import router as ai_agent_router
from .db import init_db
from .schemas import (
    BootstrapResponse,
    ProcessCsvRequest,
    ProcessCsvResponse,
    ProcessOneRequest,
    ProcessOneResponse,
    RecentResponse,
)
from .service import TicketProcessingService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="FIRE Backend", version="0.1.0")
service = TicketProcessingService()
app.include_router(ai_agent_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/bootstrap", response_model=BootstrapResponse)
def bootstrap() -> BootstrapResponse:
    try:
        stats = service.bootstrap_reference_data()
        return BootstrapResponse(offices=stats.offices, managers=stats.managers)
    except Exception as exc:
        logger.exception("Bootstrap failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/tickets/process-one", response_model=ProcessOneResponse)
def process_one(req: ProcessOneRequest) -> ProcessOneResponse:
    try:
        result = service.process_one_ticket(req.payload)
        return ProcessOneResponse(ticket=result)
    except Exception as exc:
        logger.exception("Single ticket processing failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/tickets/process-csv", response_model=ProcessCsvResponse)
def process_csv(req: ProcessCsvRequest) -> ProcessCsvResponse:
    try:
        results = service.process_csv(req.csv_path)
        return ProcessCsvResponse(count=len(results), tickets=results)
    except Exception as exc:
        logger.exception("CSV processing failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/tickets/process-csv-upload", response_model=ProcessCsvResponse)
async def process_csv_upload(file: UploadFile = File(...)) -> ProcessCsvResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    try:
        content = await file.read()
        results = service.process_csv_content(content)
        return ProcessCsvResponse(count=len(results), tickets=results)
    except Exception as exc:
        logger.exception("CSV upload processing failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/v1/tickets/recent", response_model=RecentResponse)
def recent(limit: int = 50) -> RecentResponse:
    try:
        items = service.list_recent(limit=max(1, min(500, limit)))
        return RecentResponse(items=items)
    except Exception as exc:
        logger.exception("Recent tickets query failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/v1/tickets/by-external/{external_ticket_id}")
def get_ticket_by_external(external_ticket_id: str) -> dict:
    try:
        item = service.get_ticket_by_external_id(external_ticket_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return item
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Ticket by external id query failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/v1/offices")
def list_offices() -> dict:
    try:
        return {"items": service.list_offices()}
    except Exception as exc:
        logger.exception("Offices query failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/v1/managers")
def list_managers(office_id: int | None = None) -> dict:
    try:
        return {"items": service.list_managers(office_id=office_id)}
    except Exception as exc:
        logger.exception("Managers query failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
