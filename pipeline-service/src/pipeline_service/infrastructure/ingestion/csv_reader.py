from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def read_csv_rows(path: str, required_headers: Iterable[str] | None = None) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise ValueError(f"CSV file not found: {path}")

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or []

        if required_headers:
            missing = [header for header in required_headers if header not in fieldnames]
            if missing:
                raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

        rows: list[dict[str, str]] = []
        for row in reader:
            normalized_row: dict[str, str] = {}
            for key, value in row.items():
                if key is None:
                    continue
                normalized_row[key] = (value or "")
            rows.append(normalized_row)

    return rows
