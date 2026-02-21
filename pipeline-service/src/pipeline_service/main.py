from __future__ import annotations

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from pipeline_service.application.graph.ticket_graph import build_ticket_graph
from pipeline_service.application.services.csv_ingestion_service import load_tickets_from_csv
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


def load_json_payload(file_path: str | None, use_sample: bool) -> TicketState:
    if use_sample or file_path is None:
        return SAMPLE_TICKET.copy()  # type: ignore[return-value]

    payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
    return payload


def main() -> int:
    configure_logging()

    parser = argparse.ArgumentParser(description="Run ticket LangGraph pipeline")
    parser.add_argument("--input_type", choices=["json", "csv"], default="json")
    parser.add_argument("--file", help="Path to input file", default=None)
    parser.add_argument("--sample", action="store_true", help="Use built-in sample for JSON input")
    parser.add_argument(
        "--show_timing",
        action="store_true",
        help="Print pipeline execution time summary",
    )
    args = parser.parse_args()

    show_timing = args.show_timing or os.getenv("SHOW_TIMING", "0").strip().lower() in {"1", "true", "yes", "on"}
    graph = build_ticket_graph()
    total_started_at = time.perf_counter()

    if args.input_type == "csv":
        if not args.file:
            raise ValueError("--file is required when --input_type=csv")

        tickets = load_tickets_from_csv(args.file)
        for ticket in tickets:
            started_at = time.perf_counter()
            final_state = graph.invoke(ticket)
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.info("Pipeline completed for ticket_id=%s", final_state.get("ticket_id"))
            if show_timing:
                logger.info("Ticket runtime ticket_id=%s elapsed_ms=%.2f", final_state.get("ticket_id"), elapsed_ms)
            print(json.dumps(final_state, ensure_ascii=False, indent=2))
        if show_timing:
            total_elapsed_ms = (time.perf_counter() - total_started_at) * 1000
            print(f"Pipeline total elapsed: {total_elapsed_ms:.2f} ms")
        return 0

    started_at = time.perf_counter()
    initial_state = load_json_payload(args.file, args.sample)
    final_state = graph.invoke(initial_state)
    elapsed_ms = (time.perf_counter() - started_at) * 1000

    logger.info("Pipeline completed for ticket_id=%s", final_state.get("ticket_id"))
    if show_timing:
        logger.info("Ticket runtime ticket_id=%s elapsed_ms=%.2f", final_state.get("ticket_id"), elapsed_ms)
    print(json.dumps(final_state, ensure_ascii=False, indent=2))
    if show_timing:
        total_elapsed_ms = (time.perf_counter() - total_started_at) * 1000
        print(f"Pipeline total elapsed: {total_elapsed_ms:.2f} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
