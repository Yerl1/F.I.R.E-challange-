from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState


def run(state: TicketState) -> dict[str, object]:
    country = (state.get("country") or "").upper()
    raw_address = (state.get("raw_address") or "").strip()

    if country != "KZ" or not raw_address or raw_address.lower() in {"unknown", "n/a"}:
        return {"geo_result": {"status": "fallback_5050"}}

    return {
        "geo_result": {
            "status": "ok",
            "lat": 43.238949,
            "lon": 76.889709,
        }
    }
