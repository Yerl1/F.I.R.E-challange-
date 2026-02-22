from __future__ import annotations

import datetime as dt
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Office(Base):
    __tablename__ = "offices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    address: Mapped[str] = mapped_column(Text)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    managers: Mapped[list["Manager"]] = relationship(back_populates="office")


class Manager(Base):
    __tablename__ = "managers"
    __table_args__ = (UniqueConstraint("full_name", name="uq_manager_full_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(200), index=True)
    position: Mapped[str] = mapped_column(String(120))
    office_id: Mapped[int] = mapped_column(ForeignKey("offices.id"), index=True)
    skills: Mapped[str] = mapped_column(String(250), default="")
    active_tickets: Mapped[int] = mapped_column(Integer, default=0)
    assignments_total: Mapped[int] = mapped_column(Integer, default=0)
    last_assigned_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    office: Mapped[Office] = relationship(back_populates="managers")


class TicketResult(Base):
    __tablename__ = "ticket_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_ticket_id: Mapped[str] = mapped_column(String(120), index=True)
    segment: Mapped[str] = mapped_column(String(64), default="")
    language: Mapped[str] = mapped_column(String(32), default="")
    sentiment: Mapped[str] = mapped_column(String(64), default="")
    ticket_type: Mapped[str] = mapped_column(String(120), default="")
    priority: Mapped[int] = mapped_column(Integer, default=1)
    summary: Mapped[str] = mapped_column(Text, default="")
    recommendation: Mapped[str] = mapped_column(Text, default="")
    enriched_text: Mapped[str] = mapped_column(Text, default="")
    geo_result: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("managers.id"), nullable=True)
    office_id: Mapped[int | None] = mapped_column(ForeignKey("offices.id"), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, index=True)


class RoutingState(Base):
    __tablename__ = "routing_state"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value_int: Mapped[int] = mapped_column(Integer, default=0)
