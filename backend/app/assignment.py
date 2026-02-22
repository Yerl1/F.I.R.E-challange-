from __future__ import annotations

import datetime as dt
import math
import re
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Manager, Office, RoutingState


@dataclass(frozen=True)
class AssignmentResult:
    manager_id: int | None
    office_id: int | None


def _norm_text(value: str) -> str:
    return re.sub(r"[^a-zа-я0-9]+", "", (value or "").strip().lower())


def _skills_set(skills_raw: str) -> set[str]:
    return {item.strip().upper() for item in (skills_raw or "").split(",") if item.strip()}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * radius_km * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _get_toggle(session: Session, key: str) -> int:
    state = session.get(RoutingState, key)
    if state is None:
        state = RoutingState(key=key, value_int=0)
        session.add(state)
        session.flush()
    return state.value_int


def _set_toggle(session: Session, key: str, value: int) -> None:
    state = session.get(RoutingState, key)
    if state is None:
        state = RoutingState(key=key, value_int=value)
        session.add(state)
    else:
        state.value_int = value


def _pick_round_robin(session: Session, key: str, items: list[int]) -> int:
    if len(items) == 1:
        return items[0]
    toggle = _get_toggle(session, key)
    picked = items[toggle % len(items)]
    _set_toggle(session, key, toggle + 1)
    return picked


def _is_spam(state: dict[str, object]) -> bool:
    return _norm_text(str(state.get("ticket_type", ""))) in {"спам", "spam"}


def _is_foreign_or_unknown(state: dict[str, object]) -> bool:
    country = _norm_text(str(state.get("country", "")))
    geo_result = state.get("geo_result", {})

    if country and country not in {"kz", "kazakhstan", "казахстан"}:
        return True
    if not isinstance(geo_result, dict):
        return True
    if str(geo_result.get("status", "")).lower() != "ok":
        return True
    return not (geo_result.get("lat") and geo_result.get("lon"))


def _is_foreign_country(state: dict[str, object]) -> bool:
    country = _norm_text(str(state.get("country", "")))
    if not country:
        return False
    return country not in {"kz", "kazakhstan", "казахстан"}


def _required_skills(state: dict[str, object]) -> set[str]:
    required: set[str] = set()

    segment = _norm_text(str(state.get("segment", "")))
    if segment in {"vip", "priority"}:
        required.add("VIP")

    language = _norm_text(str(state.get("language", "")))
    if language in {"eng", "en"}:
        required.add("ENG")
    elif language in {"kz", "kaz", "kk"}:
        required.add("KZ")

    return required


def _requires_head_specialist_for_data_change(state: dict[str, object]) -> bool:
    ticket_type = _norm_text(str(state.get("ticket_type", "")))
    return ticket_type in {"сменаданных", "datachange"}


def _office_total_load(managers: Iterable[Manager], office_id: int) -> int:
    return sum(m.active_tickets for m in managers if m.office_id == office_id)


def _find_5050_offices(session: Session) -> list[Office]:
    offices = session.scalars(select(Office)).all()
    by_norm = {_norm_text(office.name): office for office in offices}
    astana = by_norm.get("астана")
    almaty = by_norm.get("алматы")
    items = [office for office in [astana, almaty] if office is not None]
    return items


def _pick_office_5050(session: Session) -> int | None:
    offices = _find_5050_offices(session)
    if not offices:
        return None
    ids = [office.id for office in offices]
    return _pick_round_robin(session, "office_rr_astana_almaty", ids)


def _city_candidate_offices(offices: list[Office], city: str) -> list[Office]:
    city_norm = _norm_text(city)
    if not city_norm:
        return []
    candidates = []
    for office in offices:
        office_name = _norm_text(office.name)
        office_address = _norm_text(office.address)
        if city_norm and (city_norm in office_name or city_norm in office_address):
            candidates.append(office)
    return candidates


def _extract_city_hint_from_state(state: dict[str, object]) -> str:
    candidates = [
        str(state.get("city", "")),
        str(state.get("raw_address", "")),
        str(state.get("raw_text", "")),
        str(state.get("enriched_text", "")),
    ]
    text = " ".join(candidates).lower()
    if "астан" in text or "astana" in text:
        return "Астана"
    if "алмат" in text or "almat" in text:
        return "Алматы"
    return ""


def _pick_known_office(session: Session, state: dict[str, object]) -> int | None:
    offices = session.scalars(select(Office)).all()
    if not offices:
        return None

    managers = session.scalars(select(Manager)).all()
    geo_result = state.get("geo_result", {})
    city = str(state.get("city", ""))

    city_matches = _city_candidate_offices(offices, city)
    candidates = city_matches or offices

    # 1) If coordinates are available, prioritize nearest offices.
    lat = None
    lon = None
    if isinstance(geo_result, dict):
        lat = geo_result.get("lat")
        lon = geo_result.get("lon")

    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        with_coords = [o for o in candidates if o.lat is not None and o.lon is not None]
        if with_coords:
            with_dist = [
                (o, _haversine_km(float(lat), float(lon), float(o.lat), float(o.lon)))
                for o in with_coords
            ]
            nearest_dist = min(d for _, d in with_dist)
            # Keep near-equivalent offices (within 5km), then use load + RR.
            near = [o for o, d in with_dist if d - nearest_dist <= 5.0]
            candidates = near or [min(with_dist, key=lambda x: x[1])[0]]

    # 2) Balance by office load.
    loads = {o.id: _office_total_load(managers, o.id) for o in candidates}
    min_load = min(loads.values())
    least_loaded = [office.id for office in candidates if loads[office.id] == min_load]
    return _pick_round_robin(session, "office_rr_known_load", sorted(least_loaded))


def _pick_manager_for_office(
    session: Session,
    office_id: int,
    required_skills: set[str],
    require_head_specialist: bool,
) -> Manager | None:
    managers = session.scalars(select(Manager).where(Manager.office_id == office_id)).all()
    if not managers:
        return None

    eligible: list[Manager] = []
    for manager in managers:
        skills = _skills_set(manager.skills)
        if not required_skills.issubset(skills):
            continue
        if require_head_specialist:
            position = _norm_text(manager.position)
            if "глав" not in position and "head" not in position:
                continue
        eligible.append(manager)
    if not eligible:
        return None

    eligible.sort(
        key=lambda m: (
            m.active_tickets,
            m.last_assigned_at or dt.datetime(1970, 1, 1),
            m.id,
        )
    )
    # Pick only two least loaded candidates, then alternate by round-robin.
    rr_pool = eligible[:2]
    picked_id = _pick_round_robin(
        session,
        key=(
            f"manager_rr_office_{office_id}_"
            f"{'_'.join(sorted(required_skills)) or 'base'}_"
            f"{'head' if require_head_specialist else 'all'}"
        ),
        items=[m.id for m in rr_pool],
    )
    return next((m for m in rr_pool if m.id == picked_id), None)


def assign_manager(session: Session, state: dict[str, object]) -> AssignmentResult:
    # 1) Spam never gets assignment.
    if _is_spam(state):
        return AssignmentResult(manager_id=None, office_id=None)

    city_hint = _extract_city_hint_from_state(state)
    if city_hint and not str(state.get("city", "")).strip():
        state["city"] = city_hint

    # 2) Unknown/foreign -> strict 50/50 between Astana and Almaty.
    # If city is explicitly present in text (e.g. "я из Астаны"), treat as known.
    unknown_or_foreign = _is_foreign_or_unknown(state)
    if _is_foreign_country(state):
        unknown_or_foreign = True
    elif city_hint:
        unknown_or_foreign = False

    if unknown_or_foreign:
        office_id = _pick_office_5050(session)
    else:
        # 3) Known address -> nearest office + load balancing + round-robin.
        office_id = _pick_known_office(session, state)

    if office_id is None:
        return AssignmentResult(manager_id=None, office_id=None)

    required_skills = _required_skills(state)
    manager = _pick_manager_for_office(
        session,
        office_id=office_id,
        required_skills=required_skills,
        require_head_specialist=_requires_head_specialist_for_data_change(state),
    )
    if manager is None:
        # Keep office for visibility even if no suitable manager found.
        return AssignmentResult(manager_id=None, office_id=office_id)

    manager.active_tickets += 1
    manager.assignments_total += 1
    manager.last_assigned_at = dt.datetime.utcnow()
    return AssignmentResult(manager_id=manager.id, office_id=manager.office_id)
