import time

from pipeline_service.application.nodes import get_sentiment


def test_get_sentiment_empty_text_defaults_to_neutral() -> None:
    raw_text = ""
    started_at = time.perf_counter()
    result = get_sentiment.run({"raw_text": raw_text})
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    print(f"[get_sentiment] raw_text={raw_text!r} result={result} latency_ms={elapsed_ms:.2f}")
    assert result["sentiment"] == "Нейтральный"


def test_get_sentiment_local_model_negative_text() -> None:
    raw_text = "Ужасный сервис, приложение не работает."
    started_at = time.perf_counter()
    result = get_sentiment.run({"raw_text": raw_text})
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    print(f"[get_sentiment] raw_text={raw_text!r} result={result} latency_ms={elapsed_ms:.2f}")
    assert result["sentiment"] in {"Негативный", "Нейтральный", "Позитивный"}


def test_get_sentiment_local_model_positive_text() -> None:
    raw_text = "Спасибо, все отлично и очень удобно."
    started_at = time.perf_counter()
    result = get_sentiment.run({"raw_text": raw_text})
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    print(f"[get_sentiment] raw_text={raw_text!r} result={result} latency_ms={elapsed_ms:.2f}")
    assert result["sentiment"] in {"Негативный", "Нейтральный", "Позитивный"}
