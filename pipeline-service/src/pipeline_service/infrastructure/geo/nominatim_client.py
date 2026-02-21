from __future__ import annotations

from typing import Any

import requests


class NominatimClient:
    def __init__(self, base_url: str, user_agent: str, timeout_s: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s
        self._headers = {
            "User-Agent": user_agent,
            "Accept": "*/*",
        }

    def geocode(self, query: str, country_codes: str = "kz") -> dict[str, Any] | None:
        result = self.geocode_detailed(query=query, country_codes=country_codes)
        return result["result"]

    def geocode_detailed(self, query: str, country_codes: str = "kz") -> dict[str, Any]:
        out: dict[str, Any] = {
            "result": None,
            "first_candidate": None,
            "error": None,
        }
        response = requests.get(
            f"{self._base_url}/search",
            params={
                "q": query,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 3,
                "countrycodes": country_codes,
            },
            headers=self._headers,
            timeout=(0.5, min(3.0, self._timeout_s)),
        )
        try:
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list) or not payload:
                return out

            first = payload[0]
            if isinstance(first, dict):
                out["first_candidate"] = {
                    "display_name": str(first.get("display_name", "")),
                    "type": str(first.get("type", "")),
                    "category": str(first.get("category", "")),
                    "country_code": str((first.get("address") or {}).get("country_code", "")),
                }

            for item in payload:
                if not isinstance(item, dict):
                    continue
                address = item.get("address")
                country_code = ""
                if isinstance(address, dict):
                    country_code = str(address.get("country_code", "")).lower()
                if country_code != "kz":
                    continue

                lat = item.get("lat")
                lon = item.get("lon")
                if lat is None or lon is None:
                    continue
                try:
                    lat_v = float(lat)
                    lon_v = float(lon)
                except (TypeError, ValueError):
                    continue

                out["result"] = {
                    "lat": lat_v,
                    "lon": lon_v,
                    "display_name": str(item.get("display_name", "")),
                    "raw": item,
                }
                return out
            return out
        except Exception as exc:
            out["error"] = f"{type(exc).__name__}: {exc}"
            return out
