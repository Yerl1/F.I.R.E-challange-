from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState


def run(state: TicketState) -> dict[str, object]:
    text = (state.get("raw_text") or "").lower()
    sentiment = "Негативный" if any(x in text for x in ["не ", "ошибка", "проблем"]) else "Нейтральный"
    return {"sentiment": sentiment}
