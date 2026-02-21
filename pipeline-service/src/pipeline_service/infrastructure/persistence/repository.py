from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Protocol

from pipeline_service.settings import get_settings


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
