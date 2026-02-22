from __future__ import annotations

from pipeline_service.application.state.ticket_state import TicketState

def _build_location(state: TicketState) -> str:
    country = (state.get("country") or "").strip()
    region = (state.get("region") or "").strip()
    city = (state.get("city") or "").strip()
    street = (state.get("street") or "").strip()
    house = (state.get("house") or "").strip()

    parts: list[str] = []
    if country:
        parts.append(country)
    if region:
        parts.append(region)
    if city:
        parts.append(city)
    street_house = " ".join([p for p in [street, house] if p]).strip()
    if street_house:
        parts.append(street_house)

    return ", ".join(parts)


def run(state: TicketState) -> dict[str, object]:
    raw_text = (state.get("raw_text") or "").strip()
    extracted_text = (state.get("extracted_text") or "").strip()
    location = _build_location(state)

    blocks: list[str] = []
    if raw_text:
        blocks.append(f"[TEXT]\n{raw_text}")
    if location:
        blocks.append(f"[LOCATION]\n{location}")
    if extracted_text:
        blocks.append(f"[OCR]\n{extracted_text}")

    enriched_text = "\n\n".join(blocks).strip()

    return {"enriched_text": enriched_text}
