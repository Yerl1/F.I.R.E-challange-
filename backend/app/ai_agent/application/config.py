from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentSettings:
    ollama_base_url: str
    ollama_model: str
    default_days_range: int
    max_rows: int
    sql_timeout_seconds: float
    ollama_timeout_seconds: float


def get_agent_settings() -> AgentSettings:
    return AgentSettings(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
        ollama_model=os.getenv(
            "AI_AGENT_OLLAMA_MODEL",
            os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct-q4_K_M"),
        ),
        default_days_range=max(1, int(os.getenv("DEFAULT_DAYS_RANGE", "30"))),
        max_rows=max(1, int(os.getenv("MAX_ROWS", "500"))),
        sql_timeout_seconds=max(0.5, float(os.getenv("SQL_TIMEOUT_SECONDS", "5.0"))),
        ollama_timeout_seconds=max(0.5, float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30.0"))),
    )
