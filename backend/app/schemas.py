from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProcessOneRequest(BaseModel):
    payload: dict[str, Any]


class ProcessCsvRequest(BaseModel):
    csv_path: str | None = None


class BootstrapResponse(BaseModel):
    offices: int
    managers: int


class ProcessCsvResponse(BaseModel):
    count: int
    tickets: list[dict[str, Any]]


class ProcessOneResponse(BaseModel):
    ticket: dict[str, Any]


class RecentResponse(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)
