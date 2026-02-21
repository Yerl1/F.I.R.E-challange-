from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    request_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))
    mock_llm: bool = os.getenv("MOCK_LLM", "1") in {"1", "true", "True"}
    persist_dir: str = os.getenv("PERSIST_DIR", "/tmp")


def get_settings() -> Settings:
    return Settings()
