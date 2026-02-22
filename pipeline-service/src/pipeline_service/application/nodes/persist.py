from __future__ import annotations

import logging

from pipeline_service.application.state.ticket_state import TicketState
from pipeline_service.infrastructure.persistence.repository import build_ticket_repository

_repository = build_ticket_repository()
logger = logging.getLogger(__name__)


def run(state: TicketState) -> dict[str, object]:
    persist_id = _repository.save(dict(state))
    logger.info(
        "Persisted ticket ticket_id=%s persist_id=%s",
        state.get("ticket_id"),
        persist_id,
    )
    return {"persist_id": persist_id}
