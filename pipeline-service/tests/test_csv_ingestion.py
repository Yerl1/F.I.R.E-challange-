from __future__ import annotations

from pathlib import Path

from pipeline_service.application.services.csv_ingestion_service import load_tickets_from_csv


def test_load_tickets_from_csv_maps_expected_fields(tmp_path: Path) -> None:
    csv_content = """GUID клиента,Пол клиента,Дата рождения,Описание,Вложения,Сегмент клиента,Страна,Область,Населённый пункт,Улица,Дом
fe44694a-10ed-f011-8406-0022481ba5f0,Мужской,1998-10-02 0:00,"Здравствуйте.
Покупка акций в приложении Freedom Broker
Вопрос: можно ли в приложении совершать покупки акций дробно?",,VIP,Казахстан,Алматинская,Тургень,ул. Садовая,7
"""
    file_path = tmp_path / "tickets.csv"
    file_path.write_text(csv_content, encoding="utf-8")

    tickets = load_tickets_from_csv(str(file_path))

    assert len(tickets) == 1
    assert tickets[0]["ticket_id"] == "fe44694a-10ed-f011-8406-0022481ba5f0"
    assert "Покупка акций" in tickets[0]["raw_text"]
    assert "Казахстан" in tickets[0]["raw_address"]
