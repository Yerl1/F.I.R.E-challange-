from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState


def run(state: TicketState) -> dict[str, object]:
    errors = list(state.get("errors", []))
    return {"errors": errors}
