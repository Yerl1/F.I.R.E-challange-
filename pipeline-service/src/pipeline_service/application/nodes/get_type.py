from __future__ import annotations

import logging
import os
import warnings
from functools import lru_cache
from pathlib import Path

from pipeline_service.application.state.ticket_state import TicketState

TICKET_TYPES = [
    "Жалоба",
    "Смена данных",
    "Консультация",
    "Претензия",
    "Неработоспособность приложения",
    "Мошеннические действия",
    "Спам",
]

DEFAULT_TICKET_TYPE = "Консультация"
MAX_TEXT_LENGTH = 600
LOCAL_MODEL_PATH = os.getenv("TYPE_MODEL_PATH", "models/type_recognition")
_PROJECT_ROOT = Path(__file__).resolve().parents[4]

_LABEL_TO_TICKET_TYPE = {
    "complaint": "Жалоба",
    "data_change": "Смена данных",
    "consultation": "Консультация",
    "claim": "Претензия",
    "app_not_working": "Неработоспособность приложения",
    "fraud": "Мошеннические действия",
    "spam": "Спам",
    "жалоба": "Жалоба",
    "смена данных": "Смена данных",
    "консультация": "Консультация",
    "претензия": "Претензия",
    "неработоспособность приложения": "Неработоспособность приложения",
    "мошеннические действия": "Мошеннические действия",
    "спам": "Спам",
    "label_0": "Жалоба",
    "label_1": "Смена данных",
    "label_2": "Консультация",
    "label_3": "Претензия",
    "label_4": "Неработоспособность приложения",
    "label_5": "Мошеннические действия",
    "label_6": "Спам",
}

logger = logging.getLogger(__name__)

try:
    from sklearn.exceptions import InconsistentVersionWarning as _SklearnVersionWarning
except Exception:  # pragma: no cover - fallback for older/newer sklearn variants
    _SklearnVersionWarning = Warning


def _resolve_model_path(model_path_value: str) -> Path:
    model_path = Path(model_path_value).expanduser()
    if model_path.is_absolute():
        return model_path

    cwd_path = (Path.cwd() / model_path).resolve()
    if cwd_path.exists():
        return cwd_path

    project_path = (_PROJECT_ROOT / model_path).resolve()
    return project_path


def _resolve_existing_model_path(model_path_value: str) -> Path:
    primary = _resolve_model_path(model_path_value)
    if primary.exists():
        return primary

    candidates = [
        (_PROJECT_ROOT / "models" / "type_recognition").resolve(),
        (_PROJECT_ROOT.parent / "type_recognition").resolve(),
        (_PROJECT_ROOT.parent / "type_recognition" / "xlmr_model").resolve(),
    ]
    for path in candidates:
        if path.exists():
            return path
    return primary


@lru_cache(maxsize=1)
def _get_local_components():
    import joblib
    import torch
    from transformers import AutoTokenizer
    from transformers.models.xlm_roberta.configuration_xlm_roberta import XLMRobertaConfig
    from transformers.models.xlm_roberta.modeling_xlm_roberta import (
        XLMRobertaForSequenceClassification,
    )

    model_path = _resolve_existing_model_path(LOCAL_MODEL_PATH)
    if not model_path.exists():
        raise RuntimeError(f"Type model path does not exist: {model_path}")
    if not model_path.is_dir():
        raise RuntimeError(f"Type model path is not a directory: {model_path}")

    artifact_dir = model_path.parent if model_path.name.lower() == "xlmr_model" else model_path
    tokenizer_dir = model_path
    if not (tokenizer_dir / "tokenizer.json").exists():
        nested_tokenizer_dir = artifact_dir / "xlmr_model"
        if (nested_tokenizer_dir / "tokenizer.json").exists():
            tokenizer_dir = nested_tokenizer_dir

    label_encoder_path = artifact_dir / "label_encoder.pkl"
    if not label_encoder_path.exists():
        raise RuntimeError(f"Type label encoder does not exist: {label_encoder_path}")

    weights_path = artifact_dir / "best_model.pt"
    if not weights_path.exists():
        alt_weights = artifact_dir / "xlmr_final.pt"
        if alt_weights.exists():
            weights_path = alt_weights
        else:
            raise RuntimeError(
                f"Type model weights do not exist: {weights_path} or {alt_weights}"
            )

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=_SklearnVersionWarning,
            message=r"Trying to unpickle estimator LabelEncoder from version .*",
        )
        label_encoder = joblib.load(str(label_encoder_path))
    num_labels = len(getattr(label_encoder, "classes_", []))
    if num_labels <= 0:
        raise RuntimeError(f"Type label encoder has no classes: {label_encoder_path}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir), local_files_only=True)

    # Build model with XLM-R base architecture so checkpoint tensor shapes match.
    model_config = XLMRobertaConfig.from_pretrained(
        "xlm-roberta-base",
        num_labels=num_labels,
    )
    model = XLMRobertaForSequenceClassification(model_config)
    state_dict = torch.load(str(weights_path), map_location=device)
    if isinstance(state_dict, dict) and "state_dict" in state_dict:
        state_dict = state_dict["state_dict"]
    if not isinstance(state_dict, dict):
        raise RuntimeError(f"Unexpected state_dict format in {weights_path}")

    cleaned_state_dict = {}
    for key, value in state_dict.items():
        cleaned_key = key[7:] if key.startswith("module.") else key
        cleaned_state_dict[cleaned_key] = value

    model.load_state_dict(cleaned_state_dict, strict=False)
    model.to(device)
    model.eval()
    return tokenizer, model, label_encoder, device


@lru_cache(maxsize=512)
def _infer_text_classification(text: str):
    import torch

    tokenizer, model, label_encoder, device = _get_local_components()
    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_TEXT_LENGTH,
        padding=True,
    )
    encoded = {key: value.to(device) for key, value in encoded.items()}
    with torch.inference_mode():
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=FutureWarning,
                message=r"`encoder_attention_mask` is deprecated.*",
            )
            logits = model(**encoded).logits
        probs = torch.nn.functional.softmax(logits, dim=-1)
        pred_idx = int(torch.argmax(probs, dim=-1).item())

    if hasattr(label_encoder, "inverse_transform"):
        label = str(label_encoder.inverse_transform([pred_idx])[0])
    else:
        label = f"label_{pred_idx}"
    return {"label": str(label)}


def _extract_label(result: object) -> str:
    if isinstance(result, list) and result:
        item = result[0]
        if isinstance(item, list) and item:
            item = item[0]
        if isinstance(item, dict):
            return str(item.get("label", ""))
        return str(getattr(item, "label", ""))

    if isinstance(result, dict):
        return str(result.get("label", ""))

    return str(getattr(result, "label", ""))


def _keyword_fallback(text: str) -> str:
    if "мошенн" in text:
        return "Мошеннические действия"
    if "не открыва" in text or "ошибка" in text:
        return "Неработоспособность приложения"
    if "спам" in text:
        return "Спам"
    return DEFAULT_TICKET_TYPE


def _map_model_label(label: str) -> str:
    normalized = label.strip().lower()
    ticket_type = _LABEL_TO_TICKET_TYPE.get(normalized, DEFAULT_TICKET_TYPE)
    if ticket_type not in TICKET_TYPES:
        return DEFAULT_TICKET_TYPE
    return ticket_type


def run(state: TicketState) -> dict[str, object]:
    text = (state.get("enriched_text") or state.get("raw_text") or "").strip()
    if not text:
        return {"ticket_type": DEFAULT_TICKET_TYPE}

    text = text[:MAX_TEXT_LENGTH]
    fallback_type = _keyword_fallback(text.lower())

    try:
        result = _infer_text_classification(text)
        label = _extract_label(result)
        ticket_type = _map_model_label(label)
    except Exception:
        logger.exception("Type recognition inference failed for local model at %s", LOCAL_MODEL_PATH)
        ticket_type = fallback_type

    return {"ticket_type": ticket_type}
