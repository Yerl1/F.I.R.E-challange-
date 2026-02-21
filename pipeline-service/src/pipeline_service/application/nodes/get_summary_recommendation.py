from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState


def run(state: TicketState) -> dict[str, object]:
    text = (state.get("raw_text") or "").strip()
    summary = f"Обращение: {text[:120]}" if text else "Обращение получено и подготовлено к обработке."
    recommendation = "Провести первичную проверку и передать в соответствующую очередь обработки."
    return {
        "summary": summary,
        "recommendation": recommendation,
    }
