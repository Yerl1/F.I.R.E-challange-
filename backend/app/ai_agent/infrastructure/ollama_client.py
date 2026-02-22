from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from ..application.errors import AnalyticsError

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout_s: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_s = timeout_s

    def generate_text(self, prompt: str) -> str:
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                with httpx.Client(timeout=self._timeout_s) as client:
                    response = client.post(f"{self._base_url}/api/generate", json=payload)
                    response.raise_for_status()
                    body = response.json()
                    text = str(body.get("response", "")).strip()
                    if not text:
                        raise AnalyticsError("llm_empty", "LLM returned empty response")
                    return text
            except Exception as exc:
                last_error = exc
                logger.warning("Ollama request failed attempt=%s error=%s", attempt, exc)
        raise AnalyticsError("llm_unavailable", "Failed to call Ollama", hint=str(last_error))

    def generate_dsl_json(self, prompt: str) -> dict[str, Any]:
        raw = self.generate_text(prompt)
        parsed = _try_parse_json(raw)
        if parsed is not None:
            return parsed

        fix_prompt = (
            "Return ONLY valid JSON object. No markdown, no comments, no text.\n"
            f"Invalid content:\n{raw}"
        )
        fixed = self.generate_text(fix_prompt)
        parsed_fixed = _try_parse_json(fixed)
        if parsed_fixed is None:
            raise AnalyticsError(
                "dsl_parse_error",
                "LLM response is not valid JSON",
                hint="Try rephrasing query with explicit metric and dimension",
            )
        return parsed_fixed


def _try_parse_json(raw: str) -> dict[str, Any] | None:
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            try:
                data = json.loads(raw[start : end + 1])
                return data if isinstance(data, dict) else None
            except Exception:
                return None
        return None
