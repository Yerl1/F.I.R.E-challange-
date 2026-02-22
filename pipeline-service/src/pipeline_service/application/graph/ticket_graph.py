from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from pipeline_service.application.nodes import (
    extract_ocr_text,
    get_enriched_data,
    get_geo_data,
    get_language,
    get_priority,
    get_sentiment,
    get_summary_recommendation,
    get_type,
    is_spam,
    ingest_data,
    persist,
    start,
    type_gate,
)
from pipeline_service.application.state.ticket_state import TicketState


def build_ticket_graph():
    def _route_after_spam_check(state: TicketState) -> str:
        if state.get("is_spam"):
            return "type_gate"
        return "get_type"

    graph = StateGraph(TicketState)

    graph.add_node("start", start.run)
    graph.add_node("ingest_data", ingest_data.run)
    graph.add_node("extract_ocr_text", extract_ocr_text.run)
    graph.add_node("get_geo_data", get_geo_data.run)
    graph.add_node("get_enriched_data", get_enriched_data.run)
    graph.add_node("get_summary_recommendation", get_summary_recommendation.run)
    graph.add_node("is_spam", is_spam.run)
    graph.add_node("get_type", get_type.run)
    graph.add_node("type_gate", type_gate.run)
    graph.add_node("get_sentiment", get_sentiment.run)
    graph.add_node("get_language", get_language.run)
    graph.add_node("get_priority", get_priority.run)
    graph.add_node("persist", persist.run)

    graph.add_edge(START, "start")
    graph.add_edge("start", "ingest_data")

    graph.add_edge("ingest_data", "extract_ocr_text")
    graph.add_edge("extract_ocr_text", "get_geo_data")
    graph.add_edge("get_geo_data", "get_enriched_data")
    graph.add_edge("get_enriched_data", "get_summary_recommendation")
    graph.add_edge("get_enriched_data", "is_spam")
    graph.add_edge("ingest_data", "get_sentiment")
    graph.add_edge("ingest_data", "get_language")
    graph.add_conditional_edges(
        "is_spam",
        _route_after_spam_check,
        path_map={
            "type_gate": "type_gate",
            "get_type": "get_type",
        },
    )
    graph.add_edge("get_type", "type_gate")

    graph.add_edge(["get_sentiment", "type_gate"], "get_priority")

    graph.add_edge(["get_priority", "get_language", "get_summary_recommendation"], "persist")

    graph.add_edge("persist", END)

    return graph.compile()
