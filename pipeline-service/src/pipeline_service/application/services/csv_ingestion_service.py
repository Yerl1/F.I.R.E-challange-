from __future__ import annotations

import logging

from pipeline_service.application.state.ticket_state import TicketState
from pipeline_service.infrastructure.ingestion.csv_reader import read_csv_rows

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "GUID клиента",
    "Пол клиента",
    "Дата рождения",
    "Описание",
    "Вложения",
    "Сегмент клиента",
    "Страна",
    "Область",
    "Населённый пункт",
    "Улица",
    "Дом",
]


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _build_raw_address(country: str, region: str, city: str, street: str, house: str) -> str:
    parts = [country, region, city, street, house]
    return ", ".join([part for part in parts if part])


def load_tickets_from_csv(path: str) -> list[TicketState]:
    rows = read_csv_rows(path, required_headers=REQUIRED_COLUMNS)
    tickets: list[TicketState] = []

    for index, row in enumerate(rows, start=1):
        ticket_id = _clean(row.get("GUID клиента"))
        if not ticket_id:
            logger.warning("Skipping row %s: empty ticket_id (GUID клиента)", index)
            continue

        country = _clean(row.get("Страна"))
        region = _clean(row.get("Область"))
        city = _clean(row.get("Населённый пункт"))
        street = _clean(row.get("Улица"))
        house = _clean(row.get("Дом"))

        raw_text = _clean(row.get("Описание"))
        raw_address = _build_raw_address(country, region, city, street, house)

        state: TicketState = {
            "ticket_id": ticket_id,
            "raw_text": raw_text,
            "raw_address": raw_address,
            "country": country,
            "region": region,
            "city": city,
            "street": street,
            "house": house,
            "gender": _clean(row.get("Пол клиента")),
            "birth_date": _clean(row.get("Дата рождения")),
            "segment": _clean(row.get("Сегмент клиента")),
            "attachments": _clean(row.get("Вложения")),
        }
        tickets.append(state)

    return tickets
