from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from pipeline_service.application.graph.ticket_graph import build_ticket_graph
from pipeline_service.application.nodes import extract_ocr_text


class _FakeClient:
    def extract_text(self, image_path: str) -> str:
        return "ORDER ERROR" if Path(image_path).exists() else ""


def _create_test_image(path: Path) -> None:
    image = Image.new("RGB", (320, 90), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 30), "ORDER ERROR", fill="black")
    image.save(path)


def test_extract_ocr_text_node_returns_text_for_image(tmp_path: Path, monkeypatch) -> None:
    image_path = tmp_path / "order_error.png"
    _create_test_image(image_path)

    monkeypatch.setattr(extract_ocr_text, "_get_ocr_client", lambda lang: _FakeClient())

    state = {
        "ticket_id": "OCR-1",
        "attachments": str(image_path),
        "raw_text": "",
        "errors": [],
    }

    result = extract_ocr_text.run(state)

    assert "extracted_text" in result
    assert result["extracted_text"].strip() != ""


def test_graph_smoke_with_ocr_attachment(tmp_path: Path, monkeypatch) -> None:
    image_path = tmp_path / "order_error.png"
    _create_test_image(image_path)

    monkeypatch.setattr(extract_ocr_text, "_get_ocr_client", lambda lang: _FakeClient())

    graph = build_ticket_graph()
    payload = {
        "ticket_id": "OCR-GRAPH-1",
        "raw_text": "Сбой при оформлении заказа.",
        "raw_address": "",
        "country": "KZ",
        "region": "Алматинская",
        "city": "Тургень",
        "street": "Садовая",
        "house": "7",
        "attachments": str(image_path),
    }

    result = graph.invoke(payload)

    assert "extracted_text" in result
    assert result["extracted_text"].strip() != ""
    assert "enriched_text" in result
    assert "[OCR]" in result["enriched_text"]
