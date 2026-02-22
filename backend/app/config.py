from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BackendSettings:
    database_url: str
    max_workers: int
    docs_dir: Path
    managers_csv_path: Path
    offices_csv_path: Path
    tickets_csv_path: Path


def _pick_data_dir(repo_root: Path) -> Path:
    explicit = os.getenv("BACKEND_DOCS_DIR")
    if explicit:
        return Path(explicit)

    data_dir = repo_root / "Data"
    docs_dir = repo_root / "docs"
    if data_dir.exists():
        return data_dir
    return docs_dir


def _pick_csv_path(primary_dir: Path, filename: str, fallback_dir: Path) -> Path:
    explicit = os.getenv(f"BACKEND_{filename.split('.')[0].upper()}_CSV")
    if explicit:
        return Path(explicit)

    primary = primary_dir / filename
    if primary.exists():
        return primary
    return fallback_dir / filename


def get_settings() -> BackendSettings:
    repo_root = Path(__file__).resolve().parents[2]
    docs_dir = _pick_data_dir(repo_root)
    fallback_docs_dir = repo_root / "docs"
    database_url = os.getenv(
        "BACKEND_DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/fire_backend",
    )
    max_workers = int(os.getenv("BACKEND_MAX_WORKERS", "4"))
    managers_csv = os.getenv("BACKEND_MANAGERS_CSV")
    offices_csv = os.getenv("BACKEND_OFFICES_CSV")
    tickets_csv = os.getenv("BACKEND_TICKETS_CSV")
    return BackendSettings(
        database_url=database_url,
        max_workers=max(1, max_workers),
        docs_dir=docs_dir,
        managers_csv_path=Path(managers_csv) if managers_csv else _pick_csv_path(docs_dir, "managers.csv", fallback_docs_dir),
        offices_csv_path=Path(offices_csv) if offices_csv else _pick_csv_path(docs_dir, "business_units.csv", fallback_docs_dir),
        tickets_csv_path=Path(tickets_csv) if tickets_csv else _pick_csv_path(docs_dir, "tickets.csv", fallback_docs_dir),
    )
