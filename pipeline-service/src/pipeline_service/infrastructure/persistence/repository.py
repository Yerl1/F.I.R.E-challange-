from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from pipeline_service.settings import get_settings

logger = logging.getLogger(__name__)


class TicketRepository(Protocol):
    def save(self, payload: dict[str, object]) -> str:
        ...


class InMemoryTicketRepository:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, object]] = {}
        settings = get_settings()
        self._persist_dir = Path(settings.persist_dir)
        self._persist_dir.mkdir(parents=True, exist_ok=True)

    def save(self, payload: dict[str, object]) -> str:
        persist_id = str(uuid.uuid4())
        self._store[persist_id] = payload

        output_path = self._persist_dir / f"ticket_{persist_id}.json"
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return persist_id


class PostgresTicketRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = self._normalize_dsn(dsn)
        if not self._dsn:
            raise RuntimeError("PERSIST_POSTGRES_DSN/BACKEND_DATABASE_URL is empty")

    @staticmethod
    def _normalize_dsn(dsn: str) -> str:
        value = (dsn or "").strip()
        if value.startswith("postgresql+psycopg://"):
            return "postgresql://" + value[len("postgresql+psycopg://") :]
        return value

    def save(self, payload: dict[str, object]) -> str:
        try:
            import psycopg
        except Exception as exc:
            raise RuntimeError(
                "psycopg is not installed, cannot persist to postgres"
            ) from exc

        ticket_id = str(payload.get("ticket_id", "") or "")
        segment = str(payload.get("segment", "") or "")
        language = str(payload.get("language", "") or "")
        sentiment = str(payload.get("sentiment", "") or "")
        ticket_type = str(payload.get("ticket_type", "") or "")
        priority = int(payload.get("priority", 1) or 1)
        summary = str(payload.get("summary", "") or "")
        recommendation = str(payload.get("recommendation", "") or "")
        enriched_text = str(payload.get("enriched_text", "") or "")
        geo_result = payload.get("geo_result", {})
        if not isinstance(geo_result, dict):
            geo_result = {}
        manager_id = payload.get("manager_id")
        office_id = payload.get("office_id")
        created_at = datetime.now(timezone.utc)

        sql = """
        INSERT INTO ticket_results (
          external_ticket_id, segment, language, sentiment, ticket_type, priority,
          summary, recommendation, enriched_text, geo_result, manager_id, office_id, payload, created_at
        )
        VALUES (
          %(external_ticket_id)s, %(segment)s, %(language)s, %(sentiment)s, %(ticket_type)s, %(priority)s,
          %(summary)s, %(recommendation)s, %(enriched_text)s, %(geo_result)s::jsonb, %(manager_id)s, %(office_id)s, %(payload)s::jsonb, %(created_at)s
        )
        RETURNING id
        """

        params = {
            "external_ticket_id": ticket_id,
            "segment": segment,
            "language": language,
            "sentiment": sentiment,
            "ticket_type": ticket_type,
            "priority": priority,
            "summary": summary,
            "recommendation": recommendation,
            "enriched_text": enriched_text,
            "geo_result": json.dumps(geo_result, ensure_ascii=False),
            "manager_id": manager_id if isinstance(manager_id, int) else None,
            "office_id": office_id if isinstance(office_id, int) else None,
            "payload": json.dumps(payload, ensure_ascii=False),
            "created_at": created_at,
        }

        with psycopg.connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
            conn.commit()

        return str(row[0]) if row and row[0] is not None else str(uuid.uuid4())


def build_ticket_repository() -> TicketRepository:
    settings = get_settings()
    mode = (settings.persist_mode or "local").strip().lower()
    if mode != "postgres":
        return InMemoryTicketRepository()

    try:
        return PostgresTicketRepository(settings.persist_postgres_dsn)
    except Exception:
        logger.exception(
            "Failed to initialize postgres persistence; falling back to local json persistence"
        )
        return InMemoryTicketRepository()
