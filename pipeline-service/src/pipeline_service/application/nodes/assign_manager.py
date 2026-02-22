from __future__ import annotations

import logging

import requests

from pipeline_service.application.state.ticket_state import TicketState
from pipeline_service.settings import get_settings

logger = logging.getLogger(__name__)


def run(state: TicketState) -> dict[str, object]:
    settings = get_settings()
    if not settings.assign_enabled:
        return {}

    if bool(state.get("is_spam")):
        return {
            "manager_id": None,
            "manager_name": None,
            "office_id": None,
            "office_name": None,
            "office_address": None,
        }

    base_url = settings.backend_base_url.rstrip("/")
    url = f"{base_url}/api/v1/tickets/assign"
    payload = {"payload": dict(state)}
    timeout = max(1, settings.backend_assign_timeout_seconds)
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        body = response.json()
        assignment = body.get("assignment", {}) if isinstance(body, dict) else {}
        if not isinstance(assignment, dict):
            logger.warning("Assign endpoint returned unexpected payload: %s", body)
            return {}
        return {
            "manager_id": assignment.get("manager_id"),
            "manager_name": assignment.get("manager_name"),
            "office_id": assignment.get("office_id"),
            "office_name": assignment.get("office_name"),
            "office_address": assignment.get("office_address"),
        }
    except Exception as exc:
        logger.warning("Assignment step failed, continuing without assignment: %s", exc)
        return {}
