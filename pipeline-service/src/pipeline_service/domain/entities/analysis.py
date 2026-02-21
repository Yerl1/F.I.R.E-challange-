from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Language = Literal["KZ", "ENG", "RU"]
Sentiment = Literal["Позитивный", "Нейтральный", "Негативный"]
TicketType = Literal[
    "Жалоба",
    "Смена данных",
    "Консультация",
    "Претензия",
    "Неработоспособность приложения",
    "Мошеннические действия",
    "Спам",
]


@dataclass(slots=True)
class GeoData:
    status: str
    lat: float | None = None
    lon: float | None = None


@dataclass(slots=True)
class SummaryRecommendation:
    summary: str
    recommendation: str
