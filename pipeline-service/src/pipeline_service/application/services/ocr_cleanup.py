from __future__ import annotations

import re

from pipeline_service.domain.services.normalization import normalize_whitespace
from pipeline_service.infrastructure.llm.ollama_client import OllamaClient

_RELEVANT_KEYWORDS = (
    "ошибка",
    "приказ",
    "сбой",
    "проблем",
    "заявк",
    "ордер",
    "покуп",
    "выставлен",
    "неработ",
)


def _is_relevant(line: str) -> bool:
    lowered = line.lower()
    return any(keyword in lowered for keyword in _RELEVANT_KEYWORDS)


def _is_garbage(line: str) -> bool:
    chars = len(line)
    if chars == 0:
        return True

    letters = sum(ch.isalpha() for ch in line)
    digits = sum(ch.isdigit() for ch in line)
    punct = sum(not ch.isalnum() and not ch.isspace() for ch in line)

    if letters < 2 and not _is_relevant(line):
        return True

    noisy_ratio = (digits + punct) / max(chars, 1)
    if noisy_ratio > 0.65 and not _is_relevant(line):
        return True

    ticker_like = re.fullmatch(r"[A-Za-z]{1,6}(?:\.[A-Za-z]{1,3})?", line)
    if ticker_like and not _is_relevant(line):
        return True

    return False


def _dedupe(lines: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for line in lines:
        key = line.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(line)
    return out


def _llm_rewrite(text: str) -> str:
    prompt = (
        "Очисти OCR-текст обращения пользователя. "
        "Удали рыночный шум, тикеры, случайные символы и мусор. "
        "Оставь только смысл проблемы в 1-3 коротких предложениях. "
        "Верни только очищенный текст без комментариев.\n\n"
        f"OCR_TEXT:\n{text}\n"
    )
    response = OllamaClient().generate(prompt=prompt)
    rewritten = normalize_whitespace(response)
    if not rewritten or rewritten.lower().startswith("stub-llm-response"):
        return ""
    return rewritten


def clean_ocr_text(raw_ocr_text: str, use_llm: bool = False) -> str:
    raw_ocr_text = raw_ocr_text or ""

    normalized_lines = [normalize_whitespace(line) for line in raw_ocr_text.splitlines()]
    normalized_lines = [line for line in normalized_lines if line]

    filtered = [line for line in normalized_lines if len(line) >= 3 and not _is_garbage(line)]
    filtered = _dedupe(filtered)

    cleaned = "\n".join(filtered[:20]).strip()
    if not cleaned:
        return ""

    if use_llm:
        try:
            llm_cleaned = _llm_rewrite(cleaned)
            if llm_cleaned:
                return llm_cleaned
        except Exception:
            pass

    return cleaned
