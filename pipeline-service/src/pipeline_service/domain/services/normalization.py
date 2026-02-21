from __future__ import annotations


def normalize_whitespace(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.split())


def normalize_country_code(country: str | None) -> str:
    if not country:
        return ""
    normalized = country.strip().upper()
    aliases = {
        "KAZAKHSTAN": "KZ",
        "KAZ": "KZ",
        "RU": "RU",
        "RUS": "RU",
        "EN": "ENG",
    }
    return aliases.get(normalized, normalized)
