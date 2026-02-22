from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path

from pipeline_service.application.state.ticket_state import TicketState

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
LOCAL_MODEL_PATH = os.getenv("SPAM_MODEL_PATH", "models/spam_detection")
MAX_TEXT_LENGTH = 600
DEFAULT_SPAM_THRESHOLD = float(os.getenv("SPAM_THRESHOLD", "0.5"))

_SPAM_KEYWORDS = (
    "spam",
    "спам",
    "розыгрыш",
    "вы выиграли",
    "бесплатно",
    "промокод",
    "ставки",
    "казино",
    "viagra",
    "crypto signal",
    "forex signal",
    "click here",
    "buy now",
)

logger = logging.getLogger(__name__)


def _resolve_model_path(model_path_value: str) -> Path:
    model_path = Path(model_path_value).expanduser()
    if model_path.is_absolute():
        return model_path

    cwd_path = (Path.cwd() / model_path).resolve()
    if cwd_path.exists():
        return cwd_path

    return (_PROJECT_ROOT / model_path).resolve()


@lru_cache(maxsize=1)
def _model_path_exists() -> bool:
    return _resolve_model_path(LOCAL_MODEL_PATH).exists()


def _load_tokenizer(model_path: Path):
    from transformers import AutoTokenizer

    try:
        return AutoTokenizer.from_pretrained(
            str(model_path),
            local_files_only=True,
            use_fast=True,
        )
    except ValueError as exc:
        if "Tokenizer class TokenizersBackend" not in str(exc):
            raise

        from transformers import PreTrainedTokenizerFast

        tokenizer_file = model_path / "tokenizer.json"
        if not tokenizer_file.exists():
            raise RuntimeError(
                f"Unsupported tokenizer_class and tokenizer.json not found: {model_path}"
            ) from exc

        tokenizer = PreTrainedTokenizerFast(tokenizer_file=str(tokenizer_file))
        tokenizer_config = model_path / "tokenizer_config.json"
        if tokenizer_config.exists():
            try:
                cfg = json.loads(tokenizer_config.read_text(encoding="utf-8"))
                for key in (
                    "bos_token",
                    "eos_token",
                    "unk_token",
                    "sep_token",
                    "pad_token",
                    "cls_token",
                    "mask_token",
                ):
                    value = cfg.get(key)
                    if value:
                        setattr(tokenizer, key, value)
            except Exception:
                logger.debug(
                    "Failed to apply tokenizer_config fallback for %s",
                    model_path,
                    exc_info=True,
                )
        return tokenizer


@lru_cache(maxsize=1)
def _get_local_components():
    from transformers import AutoModelForSequenceClassification

    model_path = _resolve_model_path(LOCAL_MODEL_PATH)
    if not model_path.exists():
        raise RuntimeError(f"Spam model path does not exist: {model_path}")
    if not model_path.is_dir():
        raise RuntimeError(f"Spam model path is not a directory: {model_path}")

    tokenizer = _load_tokenizer(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(
        str(model_path),
        local_files_only=True,
    )
    model.eval()
    return tokenizer, model


@lru_cache(maxsize=1)
def _model_ready() -> bool:
    if not _model_path_exists():
        logger.warning(
            "Spam model path does not exist, using keyword fallback only: %s",
            _resolve_model_path(LOCAL_MODEL_PATH),
        )
        return False

    try:
        _get_local_components()
        return True
    except Exception:
        logger.warning(
            "Spam model is not loadable, using keyword fallback only: %s",
            _resolve_model_path(LOCAL_MODEL_PATH),
            exc_info=True,
        )
        return False


@lru_cache(maxsize=512)
def _infer_spam_probability(text: str) -> float:
    import torch

    tokenizer, model = _get_local_components()
    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_TEXT_LENGTH,
    )
    with torch.inference_mode():
        logits = model(**encoded).logits
        probs = torch.nn.functional.softmax(logits, dim=-1)
        pred_idx = int(torch.argmax(probs, dim=-1).item())
        pred_score = float(probs[0, pred_idx].item())

    id2label = getattr(model.config, "id2label", {}) or {}
    label = str(id2label.get(pred_idx, f"label_{pred_idx}")).lower()
    if "spam" in label or label == "label_1":
        return pred_score
    if "nospam" in label or "ham" in label or label == "label_0":
        return 1.0 - pred_score
    return float(probs[0, 1].item()) if probs.shape[-1] > 1 else pred_score


def _keyword_is_spam(text: str) -> bool:
    return any(keyword in text for keyword in _SPAM_KEYWORDS)


def run(state: TicketState) -> dict[str, object]:
    text = (state.get("enriched_text") or state.get("raw_text") or "").lower().strip()
    if not text:
        return {"is_spam": False}

    text = text[:MAX_TEXT_LENGTH]
    if _keyword_is_spam(text):
        return {"is_spam": True, "ticket_type": "Спам"}

    if not _model_ready():
        return {"is_spam": False}

    try:
        spam_probability = _infer_spam_probability(text)
        if spam_probability >= DEFAULT_SPAM_THRESHOLD:
            return {"is_spam": True, "ticket_type": "Спам"}
    except Exception:
        logger.warning(
            "Spam detection inference failed for local model at %s",
            LOCAL_MODEL_PATH,
            exc_info=True,
        )

    return {"is_spam": False}

