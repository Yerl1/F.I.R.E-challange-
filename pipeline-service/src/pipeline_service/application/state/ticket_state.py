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

    gender: str
    birth_date: str
    segment: str
    attachments: str
    extracted_text: str

    geo_result: dict[str, object]
    enriched_text: str

    language: str
    sentiment: str
    is_spam: bool
    ticket_type: str

    summary: str
    recommendation: str
    priority: int
    manager_id: int
    manager_name: str
    office_id: int
    office_name: str
    office_address: str

    persist_id: str
    errors: NotRequired[list[str]]
