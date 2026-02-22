from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv(
        "PIPELINE_OLLAMA_MODEL",
        os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
    )
    request_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))
    mock_llm: bool = os.getenv("MOCK_LLM", "1") in {"1", "true", "True"}
    perf_mode: bool = os.getenv("PERF_MODE", "0") in {"1", "true", "True"}
    ollama_num_predict: int = int(os.getenv("OLLAMA_NUM_PREDICT", "0"))
    ollama_num_ctx: int = int(os.getenv("OLLAMA_NUM_CTX", "0"))
    ollama_keep_alive: str = os.getenv("OLLAMA_KEEP_ALIVE", "10m")
    persist_dir: str = os.getenv("PERSIST_DIR", "/tmp")
    persist_mode: str = os.getenv("PERSIST_MODE", "local")
    persist_postgres_dsn: str = os.getenv(
        "PERSIST_POSTGRES_DSN",
        os.getenv("BACKEND_DATABASE_URL", ""),
    )
    assign_enabled: bool = os.getenv("ASSIGN_ENABLED", "0") in {"1", "true", "True"}
    backend_base_url: str = os.getenv("BACKEND_BASE_URL", "http://localhost:8001")
    backend_assign_timeout_seconds: int = int(os.getenv("BACKEND_ASSIGN_TIMEOUT_SECONDS", "15"))


def get_settings() -> Settings:
    return Settings()
