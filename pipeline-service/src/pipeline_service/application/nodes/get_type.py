from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState

TICKET_TYPES = [
    "Жалоба",
    "Смена данных",
    "Консультация",
    "Претензия",
    "Неработоспособность приложения",
    "Мошеннические действия",
    "Спам",
]


def run(state: TicketState) -> dict[str, object]:
    text = (state.get("enriched_text") or state.get("raw_text") or "").lower()
    if "мошенн" in text:
        ticket_type = "Мошеннические действия"
    elif "не открыва" in text or "ошибка" in text:
        ticket_type = "Неработоспособность приложения"
    elif "спам" in text:
        ticket_type = "Спам"
    else:
        ticket_type = "Консультация"

    if ticket_type not in TICKET_TYPES:
        ticket_type = "Консультация"
    return {"ticket_type": ticket_type}
