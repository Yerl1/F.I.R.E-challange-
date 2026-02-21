from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState


def run(state: TicketState) -> dict[str, object]:
    text = state.get("raw_text", "")
    if any("a" <= c.lower() <= "z" for c in text):
        language = "ENG"
    elif any(c in "әіңғқөұүһ" for c in text.lower()):
        language = "KZ"
    else:
        language = "RU"

    return {"language": language}
