# pipeline-service/src/pipeline_service/application/nodes/get_geo_data.py
from __future__ import annotations

import logging
import os

from pipeline_service.application.state.ticket_state import TicketState
from pipeline_service.domain.services.normalization import (
    build_normalized_address,
    extract_address_hints,
    normalize_country_code,
    normalize_whitespace,
)
from pipeline_service.infrastructure.geo import NominatimClient
from pipeline_service.infrastructure.llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


def _fallback(reason: str, country: str, region: str, city: str, street: str,
              house: str) -> dict[str, object]:
    return {
        "country": country,
        "region": region,
        "city": city,
        "street": street,
        "house": house,
        "geo_result": {
            "status": "fallback_5050",
            "reason": reason,
        },
    }


def _env_true(name: str, default: str = "0") -> bool:
    return os.getenv(name,
                     default).strip().lower() in {"1", "true", "yes", "on"}


def _build_query_variants(
    country: str,
    region: str,
    city: str,
    street: str,
    house: str,
    raw_address: str,
    llm_query: str,
) -> list[str]:
    variants: list[str] = []

    if llm_query:
        variants.append(llm_query)

    if city and region and street and house:
        variants.append(f"{city}, {region}, Казахстан, {street} {house}")
    if city and region and street:
        variants.append(f"{city}, {region}, Казахстан, {street}")
    if city and region:
        variants.append(f"{city}, {region}, Казахстан")
    if city:
        variants.append(f"{city}, Казахстан")
    if raw_address:
        variants.append(raw_address)

    normalized_address = build_normalized_address(country, region, city, street, house)
    if normalized_address:
        variants.append(normalized_address)

    unique: list[str] = []
    seen: set[str] = set()
    for item in variants:
        query = normalize_whitespace(item)
        if not query:
            continue
        key = query.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(query)
    return unique


def _is_locality_level_hit(result: dict[str, object], city: str) -> bool:
    raw = result.get("raw")
    if not isinstance(raw, dict):
        return False
    address = raw.get("address")
    if not isinstance(address, dict):
        return False
    display_name = str(raw.get("display_name", "")).lower()
    city_lower = city.lower()
    locality_keys = ("city", "town", "village", "hamlet", "municipality", "county", "state")
    has_locality = any(normalize_whitespace(address.get(key)).lower() == city_lower for key in locality_keys)
    return has_locality or (city_lower and city_lower in display_name)


def _normalize_query_with_llm(
    country: str,
    region: str,
    city: str,
    street: str,
    house: str,
    raw_address: str,
    raw_text: str,
) -> str:
    if not _env_true("GEO_USE_LLM_NORMALIZATION", "1"):
        return ""

    prompt = (
        "Нормализуй адрес для геокодирования в Казахстане. "
        "Верни только одну строку адреса без пояснений. "
        "Используй формат: '<город>, <область>, Казахстан, <улица> <дом>' если возможно.\n\n"
        f"country={country}\n"
        f"region={region}\n"
        f"city={city}\n"
        f"street={street}\n"
        f"house={house}\n"
        f"raw_address={raw_address}\n"
        f"raw_text={raw_text}\n"
    )
    try:
        response = OllamaClient().generate(prompt=prompt)
        normalized = normalize_whitespace(response.splitlines()[0] if response else "")
        if not normalized or normalized.lower().startswith("stub-llm-response"):
            return ""
        return normalized
    except Exception:
        return ""


def run(state: TicketState) -> dict[str, object]:
    try:
        country_raw = state.get("country")
        country = normalize_country_code(country_raw)
        if not country:
            return _fallback(
                "empty_country",
                "",
                normalize_whitespace(state.get("region")),
                normalize_whitespace(state.get("city")),
                normalize_whitespace(state.get("street")),
                normalize_whitespace(state.get("house")),
            )

        if country != "KZ":
            return _fallback(
                "non_kz",
                country,
                normalize_whitespace(state.get("region")),
                normalize_whitespace(state.get("city")),
                normalize_whitespace(state.get("street")),
                normalize_whitespace(state.get("house")),
            )

        region = normalize_whitespace(state.get("region"))
        city = normalize_whitespace(state.get("city"))
        street = normalize_whitespace(state.get("street"))
        house = normalize_whitespace(state.get("house"))
        raw_address = normalize_whitespace(state.get("raw_address"))
        raw_text = normalize_whitespace(state.get("raw_text"))

        hints = extract_address_hints(raw_address, raw_text)
        region = region or hints.get("region", "")
        city = city or hints.get("city", "")
        street = street or hints.get("street", "")
        house = house or hints.get("house", "")

        normalized_address = build_normalized_address(country, region, city, street, house)

        has_geocode_input = bool((city and (street or house or region))
                                 or raw_address or normalized_address)
        if not has_geocode_input:
            return _fallback("empty_address", country, region, city, street,
                             house)

        if not _env_true("GEOCODER_ENABLED", "0"):
            return {
                "country": country,
                "region": region,
                "city": city,
                "street": street,
                "house": house,
                "geo_result": {
                    "status": "ok",
                    "lat": 43.238949,
                    "lon": 76.889709,
                    "source": "stub_almaty",
                    "normalized_address": normalized_address,
                },
            }

        client = NominatimClient(
            base_url=os.getenv("GEOCODER_BASE_URL",
                               "https://nominatim.openstreetmap.org"),
            user_agent=os.getenv("GEOCODER_USER_AGENT",
                                 "fire-pipeline-service/0.1"),
            timeout_s=1.5,
        )

        llm_query = _normalize_query_with_llm(
            country=country,
            region=region,
            city=city,
            street=street,
            house=house,
            raw_address=raw_address,
            raw_text=raw_text,
        )
        query_variants = _build_query_variants(
            country=country,
            region=region,
            city=city,
            street=street,
            house=house,
            raw_address=raw_address,
            llm_query=llm_query,
        )

        result = None
        attempted: list[str] = []
        for query in query_variants:
            detailed = client.geocode_detailed(query=query, country_codes="kz")
            attempted.append(query)
            logger.info(
                "Geocode attempt query=%r first_candidate=%s error=%s",
                query,
                detailed.get("first_candidate"),
                detailed.get("error"),
            )
            result = detailed.get("result")
            if result:
                break

        if not result:
            broad_query = normalize_whitespace(f"{city}, Казахстан") if city else ""
            if broad_query and broad_query not in attempted:
                detailed = client.geocode_detailed(query=broad_query, country_codes="kz")
                logger.info(
                    "Geocode broad fallback query=%r first_candidate=%s error=%s",
                    broad_query,
                    detailed.get("first_candidate"),
                    detailed.get("error"),
                )
                result = detailed.get("result")

        if not result:
            return _fallback("geocode_failed", country, region, city, street, house)

        source = "nominatim"
        if city and _is_locality_level_hit(result, city) and not (street and house):
            source = "nominatim_locality"

        return {
            "country": country,
            "region": region,
            "city": city,
            "street": street,
            "house": house,
            "geo_result": {
                "status": "ok",
                "lat": result["lat"],
                "lon": result["lon"],
                "source": source,
                "normalized_address": normalized_address,
            },
        }
    except Exception:
        return _fallback(
            "exception",
            normalize_whitespace(state.get("country")),
            normalize_whitespace(state.get("region")),
            normalize_whitespace(state.get("city")),
            normalize_whitespace(state.get("street")),
            normalize_whitespace(state.get("house")),
        )
