from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState


def run(state: TicketState) -> dict[str, object]:
    location_parts = [
        state.get("country", ""),
        state.get("region", ""),
        state.get("city", ""),
    ]
    location = ", ".join([p for p in location_parts if p])
    enriched_text = f"{state.get('raw_text', '')}\nLocation: {location}".strip()
    return {"enriched_text": enriched_text}
