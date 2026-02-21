from __future__ import annotations

import os
import re

import fasttext

from pipeline_service.application.state.ticket_state import TicketState

_DEFAULT_LANGUAGE = "RU"
_CONFIDENCE_THRESHOLD = 0.7
_MODEL_PATH = os.getenv("FASTTEXT_MODEL_PATH", "lid.176.ftz")

try:
    _FASTTEXT_MODEL = fasttext.load_model(_MODEL_PATH)
except Exception:
    _FASTTEXT_MODEL = None


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower().strip())


def run(state: TicketState) -> dict[str, object]:
    try:
        text = _normalize_text(state.get("raw_text", ""))
        if not text or _FASTTEXT_MODEL is None:
            return {"language": _DEFAULT_LANGUAGE}

        labels, scores = _FASTTEXT_MODEL.predict(text, k=1)
        if not labels or not scores:
            return {"language": _DEFAULT_LANGUAGE}

        label = str(labels[0]).replace("__label__", "")
        confidence = float(scores[0])
        if confidence < _CONFIDENCE_THRESHOLD:
            return {"language": _DEFAULT_LANGUAGE}

        mapping = {
            "ru": "RU",
            "kk": "KZ",
            "en": "ENG",
        }
        language = mapping.get(label, _DEFAULT_LANGUAGE)
    except Exception:
        language = _DEFAULT_LANGUAGE

    return {"language": language}
