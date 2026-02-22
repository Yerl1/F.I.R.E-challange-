from __future__ import annotations

import logging
import os
from pathlib import Path

from pipeline_service.application.services.ocr_cleanup import clean_ocr_text
from pipeline_service.application.state.ticket_state import TicketState
from pipeline_service.domain.services.normalization import normalize_whitespace
from pipeline_service.infrastructure.ocr import PaddleOcrClient

logger = logging.getLogger(__name__)

_OCR_CLIENTS: dict[str, PaddleOcrClient] = {}


def _append_error(state: TicketState, error_code: str) -> list[str]:
    errors = list(state.get("errors", []))
    errors.append(error_code)
    return errors


def _env_true(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _select_ocr_lang() -> str:
    configured = normalize_whitespace(os.getenv("OCR_LANG", "ru")).lower() or "ru"
    aliases = {
        "cyrillic": "ru",
        "multi_cyrillic": "ru",
        "kk": "ru",
        "kz": "ru",
    }
    return aliases.get(configured, configured)


def _get_ocr_client(lang: str) -> PaddleOcrClient:
    client = _OCR_CLIENTS.get(lang)
    if client is None:
        client = PaddleOcrClient(lang=lang)
        _OCR_CLIENTS[lang] = client
    return client


def _resolve_attachment_path(attachment_path: str) -> Path:
    path = Path(attachment_path)
    if path.is_absolute():
        return path

    attachments_dir = os.getenv("ATTACHMENTS_DIR", "").strip()
    if attachments_dir:
        return Path(attachments_dir) / path

    return Path.cwd() / path


def run(state: TicketState) -> dict[str, object]:
    attachment_path = normalize_whitespace(state.get("attachments"))
    if not attachment_path:
        return {"extracted_text": ""}

    resolved_path = _resolve_attachment_path(attachment_path)
    if not resolved_path.exists():
        return {
            "extracted_text": "",
            "errors": _append_error(state, "attachment_not_found"),
        }

    ocr_lang = _select_ocr_lang()
    raw_ocr_text = _get_ocr_client(ocr_lang).extract_text(str(resolved_path))
    best_text = clean_ocr_text(
        raw_ocr_text=raw_ocr_text,
        use_llm=_env_true("OCR_CLEAN_WITH_LLM", "0"),
    )

    logger.info(
        "OCR completed for ticket_id=%s path=%s raw_length=%s clean_length=%s lang=%s",
        state.get("ticket_id", ""),
        str(resolved_path),
        len(raw_ocr_text),
        len(best_text),
        ocr_lang,
    )

    if not best_text:
        return {
            "extracted_text": "",
            "errors": _append_error(state, "ocr_no_text"),
        }

    return {"extracted_text": best_text}
