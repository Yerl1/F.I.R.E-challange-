import time

import pytest

from pipeline_service.application.nodes import get_sentiment


pytestmark = [pytest.mark.integration]


def test_local_model_inference_returns_label() -> None:
    raw_text = """Уточните плз за что именно и когда удерживается комиссия 50 долларов
за Обслуживание бездействующих счетов?
"""
    started_at = time.perf_counter()
    result = get_sentiment.run({"raw_text": raw_text})
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    print(f"[get_sentiment_local] raw_text={raw_text!r} result={result} latency_ms={elapsed_ms:.2f}")
    assert result["sentiment"] in {"Негативный", "Нейтральный", "Позитивный"}
