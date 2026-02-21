from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Ticket:
    ticket_id: str
    raw_text: str
    raw_address: str | None = None
    country: str | None = None
    region: str | None = None
    city: str | None = None
    street: str | None = None
    house: str | None = None
