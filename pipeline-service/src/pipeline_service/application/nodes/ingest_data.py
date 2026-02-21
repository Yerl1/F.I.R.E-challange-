from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState
from pipeline_service.domain.entities.ticket import Ticket
from pipeline_service.domain.services.normalization import (
    normalize_country_code,
    normalize_whitespace,
)


def run(state: TicketState) -> dict[str, object]:
    ticket_id = normalize_whitespace(state.get("ticket_id")) or "UNKNOWN"
    raw_text = normalize_whitespace(state.get("raw_text"))
    raw_address = normalize_whitespace(state.get("raw_address"))

    ticket = Ticket(
        ticket_id=ticket_id,
        raw_text=raw_text,
        raw_address=raw_address or None,
        country=normalize_country_code(state.get("country")),
        region=normalize_whitespace(state.get("region")) or None,
        city=normalize_whitespace(state.get("city")) or None,
        street=normalize_whitespace(state.get("street")) or None,
        house=normalize_whitespace(state.get("house")) or None,
        gender=normalize_whitespace(state.get("gender")) or None,
        birth_date=normalize_whitespace(state.get("birth_date")) or None,
        segment=normalize_whitespace(state.get("segment")) or None,
        attachments=normalize_whitespace(state.get("attachments")) or None,
    )

    return {
        "ticket_id": ticket.ticket_id,
        "raw_text": ticket.raw_text,
        "raw_address": ticket.raw_address or "",
        "country": ticket.country or "",
        "region": ticket.region or "",
        "city": ticket.city or "",
        "street": ticket.street or "",
        "house": ticket.house or "",
        "gender": ticket.gender or "",
        "birth_date": ticket.birth_date or "",
        "segment": ticket.segment or "",
        "attachments": ticket.attachments or "",
    }
