from __future__ import annotations

import logging

import requests
from requests.adapters import HTTPAdapter

from pipeline_service.settings import get_settings

logger = logging.getLogger(__name__)

_SESSION = requests.Session()
_SESSION.mount("http://", HTTPAdapter(pool_connections=20, pool_maxsize=20))
_SESSION.mount("https://", HTTPAdapter(pool_connections=20, pool_maxsize=20))


class OllamaClient:
    def __init__(self) -> None:
        self._settings = get_settings()

    def generate(self, prompt: str, model: str | None = None) -> str:
        if self._settings.mock_llm:
            logger.info("MOCK_LLM=1, returning stub LLM output")
            return "stub-llm-response"

        selected_model = model or self._settings.ollama_model
        payload = {
            "model": selected_model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": self._settings.ollama_keep_alive,
        }
        options: dict[str, int] = {}
        if self._settings.ollama_num_predict > 0:
            options["num_predict"] = self._settings.ollama_num_predict
        elif self._settings.perf_mode:
            options["num_predict"] = 96
        if self._settings.ollama_num_ctx > 0:
            options["num_ctx"] = self._settings.ollama_num_ctx
        elif self._settings.perf_mode:
            options["num_ctx"] = 1024
        if options:
            payload["options"] = options

        response = _SESSION.post(
            f"{self._settings.ollama_base_url}/api/generate",
            json=payload,
            timeout=self._settings.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return str(payload.get("response", ""))
