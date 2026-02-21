from __future__ import annotations

import re

from pipeline_service.application.state.ticket_state import TicketState

_FALLBACK_SUMMARY_RU = "Обращение получено и подготовлено к обработке."
_FALLBACK_RECOMMENDATION_RU = "Проверить карточку клиента и уточнить детали обращения."
_FALLBACK_SUMMARY_EN = "Ticket received and prepared for processing."
_FALLBACK_RECOMMENDATION_EN = "Review the client profile and clarify missing ticket details."


def _normalize_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _strip_section_headers(value: str) -> str:
    text = re.sub(r"\[(TEXT|LOCATION|OCR)\]", " ", value, flags=re.IGNORECASE)
    return _normalize_text(text)


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(k in lowered for k in keywords)


def _truncate_summary(text: str, min_len: int = 200, max_len: int = 350) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text

    cut = text[:max_len]
    sentence_break = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    if sentence_break >= min_len:
        return cut[: sentence_break + 1].strip()

    word_break = cut.rfind(" ")
    if word_break > 0:
        return (cut[:word_break] + "...").strip()
    return (cut + "...").strip()


def _build_summary(text: str, english: bool) -> str:
    if not text:
        return _FALLBACK_SUMMARY_EN if english else _FALLBACK_SUMMARY_RU

    base = _truncate_summary(text[:1200])
    if len(base) < 120:
        if english:
            return f"Client reports: {base}".strip()
        return f"Суть обращения: {base}".strip()
    return base


def _build_recommendation(state: TicketState, cleaned_text: str, english: bool) -> str:
    fraud_kw = ("мошен", "списали", "взлом", "подозр", "fraud", "stolen")
    app_kw = ("не работает", "ошибка", "краш", "вылет", "error", "crash")
    data_kw = ("сменить", "изменить данные", "паспорт", "телефон", "update data")
    spam_kw = ("реклама", "спам", "рассылка", "spam")

    segment = _normalize_text(state.get("segment"))
    issue_type = _normalize_text(
        state.get("issue_type") or state.get("type") or state.get("ticket_type")
    )
    priority_score = state.get("priority_score") or state.get("priority")
    location = ", ".join([_normalize_text(state.get("city")), _normalize_text(state.get("region"))]).strip(", ")
    ocr_present = bool(_normalize_text(state.get("extracted_text")) or "[OCR]" in (state.get("enriched_text") or ""))

    if not cleaned_text:
        return _FALLBACK_RECOMMENDATION_EN if english else _FALLBACK_RECOMMENDATION_RU

    if _contains_any(cleaned_text, fraud_kw):
        rec = (
            "Проверить подозрительные операции и статусы авторизации, при необходимости временно ограничить операции. "
            "Эскалировать обращение в fraud-очередь и зафиксировать таймлайн действий клиента."
        )
    elif _contains_any(cleaned_text, app_kw):
        rec = (
            "Собрать у клиента модель устройства, версию ОС и приложения, а также шаги воспроизведения ошибки. "
            "Передать кейс в техническую поддержку с прикреплёнными артефактами."
        )
    elif _contains_any(cleaned_text, data_kw):
        rec = (
            "Провести верификацию личности клиента и подтвердить основание для изменения данных. "
            "Маршрутизировать обращение на Глав спец для выполнения изменения."
        )
    elif _contains_any(cleaned_text, spam_kw):
        rec = (
            "Пометить обращение как спам и снизить приоритет обработки. "
            "При подтверждении признаков рассылки закрыть кейс по регламенту."
        )
    else:
        rec = (
            "Провести первичную проверку обращения и уточнить недостающие детали у клиента. "
            "Передать кейс в профильную очередь в соответствии с категорией обращения."
        )

    extras: list[str] = []
    if issue_type:
        extras.append(f"Тип: {issue_type}")
    if segment:
        extras.append(f"Сегмент: {segment}")
    if priority_score is not None:
        extras.append(f"Приоритет: {priority_score}")
    if location:
        extras.append(f"Локация: {location}")
    if ocr_present:
        extras.append("Учтён текст из вложения")

    if extras:
        rec = f"{rec} {'; '.join(extras)}."

    if english:
        return (
            "Perform initial triage and confirm missing details with the client. "
            "Route the case to the responsible queue and include type/priority metadata."
        )
    return rec


def run(state: TicketState) -> dict[str, object]:
    language = _normalize_text(state.get("language")).upper()
    english = language == "ENG"

    source = state.get("enriched_text") or state.get("raw_text") or ""
    cleaned = _strip_section_headers(_normalize_text(source))

    summary = _build_summary(cleaned, english=english)
    recommendation = _build_recommendation(state, cleaned, english=english)
    return {"summary": summary, "recommendation": recommendation}
