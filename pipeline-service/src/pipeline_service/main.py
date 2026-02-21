from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from pipeline_service.application.graph.ticket_graph import build_ticket_graph
from pipeline_service.application.state.ticket_state import TicketState

logger = logging.getLogger(__name__)


SAMPLE_TICKET: dict[str, Any] = {
    "ticket_id": "TCK-1001",
    "raw_text": "Здравствуйте, приложение не открывается после обновления.",
    "raw_address": "Алматы, ул. Абая, 10",
    "country": "KZ",
    "region": "Алматинская область",
    "city": "Алматы",
    "street": "Абая",
    "house": "10",
}


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def load_payload(input_path: str | None) -> TicketState:
    if input_path is None:
        return SAMPLE_TICKET.copy()  # type: ignore[return-value]

    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    return payload


def main() -> int:
    configure_logging()

    parser = argparse.ArgumentParser(description="Run ticket LangGraph pipeline")
    parser.add_argument("--input", help="Path to ticket JSON", default=None)
    parser.add_argument("--sample", action="store_true", help="Use built-in sample")
    args = parser.parse_args()

    input_path = None if args.sample else args.input
    initial_state = load_payload(input_path)

    graph = build_ticket_graph()
    final_state = graph.invoke(initial_state)

    logger.info("Pipeline completed for ticket_id=%s", final_state.get("ticket_id"))
    print(json.dumps(final_state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
