from __future__ import annotations

import os

from pipeline_service.application.state.ticket_state import TicketState
from pipeline_service.infrastructure.llm.ollama_client import OllamaClient


def _env_true(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _fallback_enrichment(raw_text: str, extracted_text: str) -> str:
    enriched_description = raw_text
    if extracted_text:
        enriched_description = f"{enriched_description}\n\n[OCR]\n{extracted_text}".strip()
    return enriched_description


def _enrich_with_llm(raw_text: str, extracted_text: str) -> str:
    prompt = (
        "Нормализуй описание обращения пользователя.\n"
        "Правила:\n"
        "1) Убери повторы и шум.\n"
        "2) Сохрани факты и смысл.\n"
        "3) Если есть OCR-текст, аккуратно включи релевантные части.\n"
        "4) Верни только итоговый обогащенный текст без комментариев.\n\n"
        f"RAW_TEXT:\n{raw_text}\n\n"
        f"OCR_TEXT:\n{extracted_text}\n"
    )
    response = OllamaClient().generate(prompt=prompt)
    normalized = (response or "").strip()
    if not normalized or normalized.lower().startswith("stub-llm-response"):
        return ""
    return normalized


def run(state: TicketState) -> dict[str, object]:
    raw_text = (state.get("raw_text") or "").strip()
    extracted_text = (state.get("extracted_text") or "").strip()

    enriched_description = _fallback_enrichment(raw_text=raw_text, extracted_text=extracted_text)
    if _env_true("ENRICH_WITH_LLM", "0"):
        try:
            llm_enriched = _enrich_with_llm(raw_text=raw_text, extracted_text=extracted_text)
            if llm_enriched:
                enriched_description = llm_enriched
        except Exception:
            pass

    return {
        "enriched_description": enriched_description,
        "enriched_text": enriched_description,
    }
