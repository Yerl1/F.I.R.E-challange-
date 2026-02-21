from __future__ import annotations

import logging
import os
from functools import lru_cache

from pipeline_service.application.state.ticket_state import TicketState

LOCAL_MODEL_PATH = "/Users/yerlan/F.I.R.E-challange-/sentiment_2"
DEFAULT_SENTIMENT = "Нейтральный"
MAX_TEXT_LENGTH = 600
ENABLE_INT8_QUANTIZATION = os.getenv("SENTIMENT_INT8", "1") == "1"

_LABEL_TO_SENTIMENT = {
    "negative": "Негативный",
    "neutral": "Нейтральный",
    "positive": "Позитивный",
    "label_0": "Негативный",
    "label_1": "Нейтральный",
    "label_2": "Позитивный",
}

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_local_components():
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch

    model_path = LOCAL_MODEL_PATH
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    except Exception as exc:
        raise RuntimeError(
            "Failed to load local tokenizer from sentiment_2."
        ) from exc

    model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
    if ENABLE_INT8_QUANTIZATION:
        try:
            # Dynamic int8 quantization for CPU inference speedup and lower memory usage.
            model = torch.quantization.quantize_dynamic(
                model,
                {torch.nn.Linear},
                dtype=torch.qint8,
            )
            logger.info("Loaded quantized int8 sentiment model from %s", model_path)
        except Exception:
            logger.exception("Int8 quantization failed, using original fp model")

    model.eval()
    return tokenizer, model


def _extract_label(result: object) -> str:
    if isinstance(result, list) and result:
        item = result[0]
        if isinstance(item, list) and item:
            item = item[0]
        if isinstance(item, dict):
            return str(item.get("label", "neutral"))
        return str(getattr(item, "label", "neutral"))

    if isinstance(result, dict):
        return str(result.get("label", "neutral"))

    return str(getattr(result, "label", "neutral"))


@lru_cache(maxsize=512)
def _infer_text_classification(text: str):
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
        score = float(probs[0, pred_idx].item())

    id2label = getattr(model.config, "id2label", {}) or {}
    label = id2label.get(pred_idx) or id2label.get(str(pred_idx)) or f"label_{pred_idx}"
    return {"label": label, "score": score}


def _map_model_label(label: str) -> str:
    return _LABEL_TO_SENTIMENT.get(label.strip().lower(), DEFAULT_SENTIMENT)


def run(state: TicketState) -> dict[str, object]:
    text = (state.get("raw_text") or "").strip()
    if not text:
        return {"sentiment": DEFAULT_SENTIMENT}
    text = text[:MAX_TEXT_LENGTH]

    try:
        result = _infer_text_classification(text)
        label = _extract_label(result)
        sentiment = _map_model_label(label)
    except Exception as exc:
        logger.exception("Sentiment inference failed for local model at %s", LOCAL_MODEL_PATH)
        raise RuntimeError(f"Local sentiment model inference failed: {exc}") from exc

    return {"sentiment": sentiment}
