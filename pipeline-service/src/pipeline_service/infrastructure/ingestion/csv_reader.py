from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def _normalize_header(header: str) -> str:
    # Strip UTF-8 BOM from the first header and trim accidental spaces.
    return header.lstrip("\ufeff").strip()


def read_csv_rows(path: str, required_headers: Iterable[str] | None = None) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise ValueError(f"CSV file not found: {path}")

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        raw_fieldnames = reader.fieldnames or []
        normalized_fieldnames = [_normalize_header(field) for field in raw_fieldnames]
        reader.fieldnames = normalized_fieldnames

        if required_headers:
            normalized_required = [_normalize_header(header) for header in required_headers]
            missing = [header for header in normalized_required if header not in normalized_fieldnames]
            if missing:
                raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

        rows: list[dict[str, str]] = []
        for row in reader:
            normalized_row: dict[str, str] = {}
            for key, value in row.items():
                if key is None:
                    continue
                normalized_key = _normalize_header(key)
                normalized_row[normalized_key] = (value or "")
            rows.append(normalized_row)

    return rows
