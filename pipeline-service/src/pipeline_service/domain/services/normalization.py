from __future__ import annotations

import re


def normalize_whitespace(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.split())


def normalize_country_code(country: str | None) -> str | None:
    if not country:
        return None
    normalized = normalize_whitespace(country).upper()
    aliases = {
        "KZ": "KZ",
        "KAZAKHSTAN": "KZ",
        "КАЗАХСТАН": "KZ",
        "ҚАЗАҚСТАН": "KZ",
        "РК": "KZ",
        "РЕСПУБЛИКА КАЗАХСТАН": "KZ",
        "KAZ": "KZ",
        "RU": "RU",
        "RUS": "RU",
        "EN": "ENG",
    }
    return aliases.get(normalized, normalized or None)


def extract_address_hints(raw_address: str | None, raw_text: str | None) -> dict[str, str]:
    hints: dict[str, str] = {}
    candidates = [normalize_whitespace(raw_address), normalize_whitespace(raw_text)]

    region_re = re.compile(r"\b([А-Яа-яA-Za-z\- ]+?)\s+(?:обл(?:асть)?\.?)\b")
    city_re = re.compile(r"\b(?:г\.?|город[еа]?)\s*([А-Яа-яA-Za-z\- ]+)")
    street_re = re.compile(r"\b(?:ул\.?|улиц[аееы]|street|st\.)\s*([А-Яа-яA-Za-z0-9\- ]+)")
    street_alt_re = re.compile(r"\bпо\s+([А-Яа-яA-Za-z\- ]+?)\s+улиц[еы]\b")
    house_re = re.compile(r"\b(?:дом|д\.)\s*([0-9A-Za-zА-Яа-я\-\/]+)\b")

    for text in candidates:
        if not text:
            continue
        normalized_text = " ".join(text.split(","))

        if "region" not in hints:
            region_match = region_re.search(normalized_text)
            if region_match:
                hints["region"] = normalize_whitespace(region_match.group(1))
            elif "алматинск" in normalized_text.lower():
                hints["region"] = "Алматинская"

        if "city" not in hints:
            city_match = city_re.search(normalized_text)
            if city_match:
                hints["city"] = normalize_whitespace(city_match.group(1).split()[0])

        if "street" not in hints:
            street_match = street_re.search(normalized_text)
            if street_match:
                hints["street"] = normalize_whitespace(street_match.group(1).split(",")[0])
            else:
                street_alt_match = street_alt_re.search(normalized_text)
                if street_alt_match:
                    hints["street"] = normalize_whitespace(street_alt_match.group(1))

        if "house" not in hints:
            house_match = house_re.search(normalized_text)
            if house_match:
                hints["house"] = normalize_whitespace(house_match.group(1))

    return hints


def build_normalized_address(
    country: str | None,
    region: str | None,
    city: str | None,
    street: str | None,
    house: str | None,
) -> str:
    line_parts = [
        normalize_whitespace(country),
        normalize_whitespace(region),
        normalize_whitespace(city),
    ]
    street_line = normalize_whitespace(" ".join([normalize_whitespace(street), normalize_whitespace(house)]).strip())
    if street_line:
        line_parts.append(street_line)
    return ", ".join(part for part in line_parts if part)
