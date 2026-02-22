from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState


def run(state: TicketState) -> dict[str, object]:
    ticket_type = state.get("ticket_type")
    sentiment = state.get("sentiment")

    if not ticket_type or not sentiment:
        raise ValueError("get_priority requires both 'ticket_type' and 'sentiment' in state")

    base = {
        "Мошеннические действия": 9,
        "Неработоспособность приложения": 7,
        "Претензия": 6,
        "Жалоба": 5,
        "Смена данных": 4,
        "Консультация": 3,
        "Спам": 1,
    }.get(ticket_type, 3)

    if sentiment == "Негативный":
        base += 2
    elif sentiment == "Позитивный":
        base -= 1

    priority = max(1, min(10, base))
    return {"priority": priority}
