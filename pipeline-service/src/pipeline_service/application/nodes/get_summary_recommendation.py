from __future__ import annotations

import re

from pipeline_service.application.state.ticket_state import TicketState

_FALLBACK_SUMMARY_RU = "Ассистент сообщает: обращение получено и передано в обработку."
_FALLBACK_RECOMMENDATION_RU = (
    "Проверить карточку клиента и уточнить недостающие детали обращения."
)
_FALLBACK_SUMMARY_EN = (
    "Assistant summary: the request was received and routed for processing."
)
_FALLBACK_RECOMMENDATION_EN = (
    "Review the client profile and clarify missing ticket details."
)


def _normalize_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _strip_section_headers(value: str) -> str:
    text = re.sub(r"\[(TEXT|LOCATION|OCR)\]", " ", value, flags=re.IGNORECASE)
    return _normalize_text(text)


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def _short_issue_text(cleaned_text: str, max_len: int = 180) -> str:
    if not cleaned_text:
        return ""
    if len(cleaned_text) <= max_len:
        return cleaned_text
    cut = cleaned_text[:max_len]
    last_space = cut.rfind(" ")
    if last_space > 0:
        cut = cut[:last_space]
    return cut.strip() + "..."


def _extract_money_hint(text: str) -> str:
    # Examples: "15-20$", "$15-$20", "15$"
    patterns = [
        r"\$?\s*(\d{1,5})\s*[-–]\s*\$?\s*(\d{1,5})\s*\$?",
        r"\$?\s*(\d{1,5})\s*\$",
    ]
    lowered = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if not match:
            continue
        groups = [g for g in match.groups() if g]
        if len(groups) >= 2:
            return f"(около ${groups[0]}-${groups[1]})"
        if len(groups) == 1:
            return f"(около ${groups[0]})"
    return ""


def _build_summary_ru(cleaned_text: str) -> str:
    if not cleaned_text:
        return _FALLBACK_SUMMARY_RU

    lowered = cleaned_text.lower()
    # Special-case: fractional stocks request.
    if ("дробн" in lowered and "акци" in lowered) or (
        "fractional" in lowered and "stock" in lowered
    ):
        app_name = "приложение Freedom Broker" if "freedom broker" in lowered else "приложение"
        amount_hint = _extract_money_hint(cleaned_text)
        amount_part = f" при небольших суммах {amount_hint}".replace("  ", " ").strip()
        if amount_part and not amount_part.startswith("при"):
            amount_part = "при небольших суммах " + amount_part
        return (
            f"Пользователь уточняет, поддерживает ли {app_name} покупку дробных акций"
            f"{(' ' + amount_part) if amount_part else ''}. "
            "Если функция доступна, он просит дать пошаговую инструкцию "
            "по совершению такой покупки в приложении."
        ).strip()

    issue = _short_issue_text(cleaned_text)
    if _contains_any(lowered, ("можно ли", "как", "подскажите", "что делать", "инструкция")):
        return (
            "Ассистент сообщает: пользователь запрашивает разъяснение по следующему вопросу: "
            f"{issue}. Просит предоставить пошаговую инструкцию или порядок действий."
        )
    return f"Ассистент сообщает: пользователь обращается по вопросу: {issue}."


def _build_summary_en(cleaned_text: str) -> str:
    if not cleaned_text:
        return _FALLBACK_SUMMARY_EN
    issue = _short_issue_text(cleaned_text)
    return (
        "Assistant summary: the user asks for clarification on the following issue: "
        f"{issue}. The user requests actionable next steps."
    )


def _build_recommendation(state: TicketState, cleaned_text: str, english: bool) -> str:
    fraud_kw = ("мошен", "списали", "взлом", "подозр", "fraud", "stolen")
    app_kw = ("не работает", "ошибка", "краш", "вылет", "error", "crash")
    data_kw = ("сменить", "изменить данные", "паспорт", "телефон", "update data")
    spam_kw = ("реклама", "спам", "рассылка", "spam")

    segment = _normalize_text(state.get("segment"))
    issue_type = _normalize_text(state.get("issue_type") or state.get("type") or state.get("ticket_type"))
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
            "Передать кейс в техническую поддержку с прикрепленными артефактами."
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
        extras.append("Учтен текст из вложения")

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

    summary = _build_summary_en(cleaned) if english else _build_summary_ru(cleaned)
    recommendation = _build_recommendation(state, cleaned, english=english)
    return {"summary": summary, "recommendation": recommendation}
