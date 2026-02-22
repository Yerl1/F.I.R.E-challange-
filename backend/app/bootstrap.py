from __future__ import annotations

import csv
import logging
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Manager, Office
from .pipeline_integration import _ensure_pipeline_import_path

_ensure_pipeline_import_path()
from pipeline_service.infrastructure.geo.nominatim_client import NominatimClient

logger = logging.getLogger(__name__)


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows: list[dict[str, str]] = []
        for row in reader:
            cleaned: dict[str, str] = {}
            for key, value in row.items():
                cleaned[str(key).replace("\ufeff", "").strip()] = (value or "").strip()
            rows.append(cleaned)
        return rows


def _norm_header(value: str) -> str:
    return re.sub(r"[^a-zа-я0-9]+", "", (value or "").strip().lower())


def _pick(row: dict[str, str], *aliases: str) -> str:
    normalized = {_norm_header(k): v for k, v in row.items()}
    for alias in aliases:
        value = normalized.get(_norm_header(alias), "")
        if value:
            return value.strip()
    return ""


def _geocode_office(address: str) -> tuple[float | None, float | None]:
    try:
        client = NominatimClient(
            base_url="http://localhost:8080",
            user_agent="fire-backend/0.1",
            timeout_s=1.5,
        )
        detailed = client.geocode_detailed(query=address, country_codes="kz")
        result = detailed.get("result")
        if not result:
            return None, None
        return float(result["lat"]), float(result["lon"])
    except Exception:
        return None, None


def seed_offices(session: Session, offices_csv: Path) -> int:
    created_or_updated = 0
    for row in _read_csv_rows(offices_csv):
        name = _pick(row, "Офис", "office", "name")
        address = _pick(row, "Адрес", "address")
        if not name:
            continue

        office = session.scalar(select(Office).where(Office.name == name))
        lat: float | None = None
        lon: float | None = None
        if address:
            lat, lon = _geocode_office(f"{name}, {address}, Казахстан")

        if office is None:
            office = Office(name=name, address=address, lat=lat, lon=lon)
            session.add(office)
        else:
            office.address = address or office.address
            office.lat = lat if lat is not None else office.lat
            office.lon = lon if lon is not None else office.lon
        created_or_updated += 1
    session.flush()
    return created_or_updated


def seed_managers(session: Session, managers_csv: Path) -> int:
    office_by_name = {office.name: office for office in session.scalars(select(Office)).all()}
    created_or_updated = 0
    for row in _read_csv_rows(managers_csv):
        full_name = _pick(row, "ФИО", "fullname", "full_name")
        office_name = _pick(row, "Офис", "office")
        if not full_name or not office_name:
            continue

        office = office_by_name.get(office_name)
        if office is None:
            logger.warning("Skipping manager=%s unknown office=%s", full_name, office_name)
            continue

        position = _pick(row, "Должность", "position")
        skills = _pick(row, "Навыки", "skills")
        active_raw = _pick(row, "Количество обращений в работе", "active_tickets") or "0"
        try:
            active_tickets = int(active_raw)
        except ValueError:
            active_tickets = 0

        manager = session.scalar(select(Manager).where(Manager.full_name == full_name))
        if manager is None:
            manager = Manager(
                full_name=full_name,
                position=position,
                office_id=office.id,
                skills=skills,
                active_tickets=active_tickets,
            )
            session.add(manager)
        else:
            manager.position = position or manager.position
            manager.office_id = office.id
            manager.skills = skills or manager.skills
            manager.active_tickets = active_tickets
        created_or_updated += 1
    return created_or_updated
