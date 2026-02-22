from __future__ import annotations

import logging
import os
import sys
from functools import lru_cache
from pathlib import Path

from pipeline_service.application.state.ticket_state import TicketState

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
LOCAL_MODEL_PATH = os.getenv(
    "SENTIMENT_MODEL_PATH",
    "models/sentiment",
)
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


def _resolve_model_path(model_path_value: str) -> Path:
    model_path = Path(model_path_value).expanduser()
    if model_path.is_absolute():
        return model_path

    cwd_path = (Path.cwd() / model_path).resolve()
    if cwd_path.exists():
        return cwd_path

    project_path = (_PROJECT_ROOT / model_path).resolve()
    return project_path


def _ensure_torch_compile_compat(model_path: Path) -> None:
    # ModernBERT modules use @torch.compile decorators. With torch 2.3 + Python 3.12,
    # torch.compile raises at import time. Patch compile to no-op for this runtime.
    if sys.version_info < (3, 12):
        return

    config_path = model_path / "config.json"
    if not config_path.exists():
        return

    try:
        import json

        model_type = str(json.loads(config_path.read_text(encoding="utf-8")).get("model_type", "")).lower()
        if model_type != "modernbert":
            return

        import torch

        if getattr(torch, "_pipeline_compile_patched", False):
            return

        def _noop_compile(*_args, **_kwargs):
            def _decorator(fn):
                return fn

            return _decorator

        torch.compile = _noop_compile  # type: ignore[assignment]
        torch._pipeline_compile_patched = True  # type: ignore[attr-defined]
        logger.warning(
            "Applied torch.compile no-op patch for ModernBERT on Python 3.12 runtime."
        )
    except Exception:
        logger.debug("Failed to apply ModernBERT compile compatibility patch", exc_info=True)


@lru_cache(maxsize=1)
def _get_local_components():
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch

    model_path = _resolve_model_path(LOCAL_MODEL_PATH)
    _ensure_torch_compile_compat(model_path)
    if not model_path.exists():
        raise RuntimeError(f"Sentiment model path does not exist: {model_path}")
    if not model_path.is_dir():
        raise RuntimeError(f"Sentiment model path is not a directory: {model_path}")

    try:
        tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
    except Exception as exc:
        raise RuntimeError("Failed to load local tokenizer from sentiment model path.") from exc

    model = AutoModelForSequenceClassification.from_pretrained(str(model_path), local_files_only=True)
    # ModernBERT may try to enable torch.compile on CPU and emit a fallback warning.
    if hasattr(model, "config") and hasattr(model.config, "reference_compile"):
        try:
            model.config.reference_compile = False
        except Exception:
            logger.debug("Unable to disable ModernBERT reference_compile", exc_info=True)

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
    except Exception:
        logger.exception("Sentiment inference failed for local model at %s", LOCAL_MODEL_PATH)
        sentiment = DEFAULT_SENTIMENT

    return {"sentiment": sentiment}
