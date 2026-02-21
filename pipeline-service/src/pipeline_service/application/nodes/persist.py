from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState
from pipeline_service.infrastructure.persistence.repository import InMemoryTicketRepository

_repository = InMemoryTicketRepository()


def run(state: TicketState) -> dict[str, object]:
    persist_id = _repository.save(dict(state))
    return {"persist_id": persist_id}
