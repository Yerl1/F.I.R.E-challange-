from __future__ import annotations

import logging

import requests

from pipeline_service.settings import get_settings

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self) -> None:
        self._settings = get_settings()

    def generate(self, prompt: str, model: str | None = None) -> str:
        if self._settings.mock_llm:
            logger.info("MOCK_LLM=1, returning stub LLM output")
            return "stub-llm-response"

        selected_model = model or self._settings.ollama_model
        response = requests.post(
            f"{self._settings.ollama_base_url}/api/generate",
            json={
                "model": selected_model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=self._settings.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return str(payload.get("response", ""))
