from __future__ import annotations

from typing import NotRequired, TypedDict


class TicketState(TypedDict, total=False):
    ticket_id: str
    raw_text: str
    raw_address: str
    country: str
    region: str
    city: str
    street: str
    house: str

    geo_result: dict[str, object]
    enriched_text: str

    language: str
    sentiment: str
    ticket_type: str

    summary: str
    recommendation: str
    priority: int

    persist_id: str
    errors: NotRequired[list[str]]
