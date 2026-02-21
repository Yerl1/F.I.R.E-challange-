from pipeline_service.application.graph.ticket_graph import build_ticket_graph


def test_graph_smoke_run_contains_required_fields() -> None:
    graph = build_ticket_graph()

    payload = {
        "ticket_id":
        "TST-USER-CASE-1",
        "raw_text":
        ("Здравствуйте. Я живу в городе Тургень по Садовой улице и хотел спросить у вас\n"
         "Покупка акций в приложении Freedom Broker\n"
         "Вопрос: можно ли в приложении совершать покупки акций дробно (когда\n"
         "инвестируется небольшие средства 15-20$)?"),
        "raw_address":
        "",
        "country":
        "",
        "region":
        "Алматинская",
        "city":
        "",
        "street":
        "",
        "house":
        "7",
    }

    result = graph.invoke(payload)

    assert "geo_result" in result
    assert "sentiment" in result
    assert "language" in result
    assert "ticket_type" in result
    assert "summary" in result
    assert "recommendation" in result
    assert "priority" in result
    assert "persist_id" in result
    assert result["geo_result"]["status"] == "fallback_5050"
