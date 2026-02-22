from __future__ import annotations

import concurrent.futures
import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from sqlalchemy import select

from .assignment import assign_manager
from .bootstrap import seed_managers, seed_offices
from .config import get_settings
from .db import get_session
from .models import Manager, Office, TicketResult
from .pipeline_integration import _ensure_pipeline_import_path

_ensure_pipeline_import_path()
from pipeline_service.application.graph.ticket_graph import build_ticket_graph

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BootstrapStats:
    offices: int
    managers: int


class TicketProcessingService:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._graph = build_ticket_graph()

    def bootstrap_reference_data(self) -> BootstrapStats:
        with get_session() as session:
            offices = seed_offices(session, self._settings.offices_csv_path)
            managers = seed_managers(session, self._settings.managers_csv_path)
            return BootstrapStats(offices=offices, managers=managers)

    def process_one_ticket(self, payload: dict[str, Any]) -> dict[str, Any]:
        state = self._graph.invoke(payload)
        assignment_payload = self.assign_for_state(state)
        with get_session() as session:
            state.update(assignment_payload)

            ticket_row = TicketResult(
                external_ticket_id=str(state.get("ticket_id", "")),
                segment=str(state.get("segment", "")),
                language=str(state.get("language", "")),
                sentiment=str(state.get("sentiment", "")),
                ticket_type=str(state.get("ticket_type", "")),
                priority=int(state.get("priority", 1) or 1),
                summary=str(state.get("summary", "")),
                recommendation=str(state.get("recommendation", "")),
                enriched_text=str(state.get("enriched_text", "")),
                geo_result=state.get("geo_result", {}) if isinstance(state.get("geo_result"), dict) else {},
                manager_id=state.get("manager_id"),
                office_id=state.get("office_id"),
                payload=dict(state),
            )
            session.add(ticket_row)
            session.flush()
            state["db_ticket_id"] = ticket_row.id
        return state

    def assign_for_state(self, state: dict[str, Any]) -> dict[str, Any]:
        with get_session() as session:
            assignment = assign_manager(session, state)
            manager_name = None
            office_name = None
            office_address = None
            if assignment.manager_id is not None:
                manager = session.get(Manager, assignment.manager_id)
                manager_name = manager.full_name if manager else None
            if assignment.office_id is not None:
                office = session.get(Office, assignment.office_id)
                office_name = office.name if office else None
                office_address = office.address if office else None
            return {
                "manager_id": assignment.manager_id,
                "manager_name": manager_name,
                "office_id": assignment.office_id,
                "office_name": office_name,
                "office_address": office_address,
            }

    def process_csv(self, csv_path: str | Path | None = None) -> list[dict[str, Any]]:
        path = Path(csv_path) if csv_path is not None else self._settings.tickets_csv_path
        tickets = _load_tickets_from_csv_robust(path)
        return self._process_tickets_concurrently(tickets)

    def process_csv_content(self, content: bytes) -> list[dict[str, Any]]:
        with NamedTemporaryFile(suffix=".csv", delete=True) as tmp:
            tmp.write(content)
            tmp.flush()
            tickets = _load_tickets_from_csv_robust(Path(tmp.name))
        return self._process_tickets_concurrently(tickets)

    def _process_tickets_concurrently(self, tickets: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not tickets:
            return []

        results: list[dict[str, Any]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._settings.max_workers) as pool:
            futures = [pool.submit(self.process_one_ticket, ticket) for ticket in tickets]
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception:
                    logger.exception("Ticket processing failed in worker thread")
        return results

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with get_session() as session:
            rows = session.scalars(
                select(TicketResult).order_by(TicketResult.created_at.desc()).limit(limit)
            ).all()
            return [
                {
                    "id": row.id,
                    "external_ticket_id": row.external_ticket_id,
                    "status": "DONE",
                    "ticket_type": row.ticket_type,
                    "priority": row.priority,
                    "summary": row.summary,
                    "city": str((row.payload or {}).get("city", "")),
                    "manager_id": row.manager_id,
                    "manager_name": str((row.payload or {}).get("manager_name", "")),
                    "office_id": row.office_id,
                    "office_name": str((row.payload or {}).get("office_name", "")),
                    "created_at": row.created_at.isoformat(),
                }
                for row in rows
            ]

    def get_ticket_by_external_id(self, external_ticket_id: str) -> dict[str, Any] | None:
        with get_session() as session:
            row = session.scalars(
                select(TicketResult)
                .where(TicketResult.external_ticket_id == external_ticket_id)
                .order_by(TicketResult.created_at.desc())
                .limit(1)
            ).first()
            if row is None:
                return None
            payload = row.payload or {}
            office = session.get(Office, row.office_id) if row.office_id is not None else None
            geo_result = row.geo_result if isinstance(row.geo_result, dict) else {}
            normalized_address = str(geo_result.get("normalized_address", "")).strip()
            if not normalized_address:
                normalized_address = str(payload.get("raw_address", "")).strip()
            if not normalized_address:
                country = str(payload.get("country", "")).strip()
                region = str(payload.get("region", "")).strip()
                city = str(payload.get("city", "")).strip()
                street = str(payload.get("street", "")).strip()
                house = str(payload.get("house", "")).strip()
                normalized_address = ", ".join(
                    [part for part in [country, region, city, street, house] if part]
                )
            return {
                "id": row.id,
                "external_ticket_id": row.external_ticket_id,
                "status": "DONE",
                "segment": row.segment,
                "language": row.language,
                "sentiment": row.sentiment,
                "ticket_type": row.ticket_type,
                "priority": row.priority,
                "summary": row.summary,
                "recommendation": row.recommendation,
                "enriched_text": row.enriched_text,
                "geo_result": geo_result,
                "normalized_address": normalized_address,
                "manager_id": row.manager_id,
                "manager_name": str(payload.get("manager_name", "")),
                "office_id": row.office_id,
                "office_name": str(payload.get("office_name", "") or (office.name if office else "")),
                "office_address": str(payload.get("office_address", "") or (office.address if office else "")),
                "city": str(payload.get("city", "")),
                "raw_text": str(payload.get("raw_text", "")),
                "payload": payload,
                "created_at": row.created_at.isoformat(),
            }

    def list_offices(self) -> list[dict[str, Any]]:
        with get_session() as session:
            rows = session.scalars(select(Office).order_by(Office.id.asc())).all()
            return [
                {
                    "id": row.id,
                    "name": row.name,
                    "address": row.address,
                    "lat": row.lat,
                    "lon": row.lon,
                    "created_at": row.created_at.isoformat(),
                }
                for row in rows
            ]

    def list_managers(self, office_id: int | None = None) -> list[dict[str, Any]]:
        with get_session() as session:
            query = select(Manager).order_by(Manager.id.asc())
            if office_id is not None:
                query = query.where(Manager.office_id == office_id)
            rows = session.scalars(query).all()
            return [
                {
                    "id": row.id,
                    "full_name": row.full_name,
                    "position": row.position,
                    "office_id": row.office_id,
                    "skills": row.skills,
                    "active_tickets": row.active_tickets,
                    "assignments_total": row.assignments_total,
                    "created_at": row.created_at.isoformat(),
                }
                for row in rows
            ]


def _clean_header(value: str) -> str:
    return (value or "").replace("\ufeff", "").strip()


def _normalize_row_keys(row: dict[str, str]) -> dict[str, str]:
    return {_clean_header(k): (v or "").strip() for k, v in row.items()}


def _build_raw_address(country: str, region: str, city: str, street: str, house: str) -> str:
    return ", ".join([p for p in [country, region, city, street, house] if p])


def _load_tickets_from_csv_robust(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = [_normalize_row_keys(row) for row in reader]

    tickets: list[dict[str, Any]] = []
    for row in rows:
        ticket_id = row.get("GUID клиента", "").strip()
        if not ticket_id:
            continue
        country = row.get("Страна", "").strip()
        region = row.get("Область", "").strip()
        city = row.get("Населённый пункт", "").strip()
        street = row.get("Улица", "").strip()
        house = row.get("Дом", "").strip()
        raw_text = row.get("Описание", row.get("Описание ", "")).strip()

        tickets.append(
            {
                "ticket_id": ticket_id,
                "raw_text": raw_text,
                "raw_address": _build_raw_address(country, region, city, street, house),
                "country": country,
                "region": region,
                "city": city,
                "street": street,
                "house": house,
                "gender": row.get("Пол клиента", "").strip(),
                "birth_date": row.get("Дата рождения", "").strip(),
                "segment": row.get("Сегмент клиента", "").strip(),
                "attachments": row.get("Вложения", "").strip(),
            }
        )
    return tickets
