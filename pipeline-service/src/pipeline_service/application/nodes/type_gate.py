from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState

DEFAULT_TICKET_TYPE = "Консультация"


def run(state: TicketState) -> dict[str, object]:
    ticket_type = (state.get("ticket_type") or "").strip()
    if ticket_type:
        return {}
    return {"ticket_type": DEFAULT_TICKET_TYPE}
