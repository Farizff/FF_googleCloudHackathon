from __future__ import annotations

from copy import deepcopy
from datetime import date as date_type
from datetime import datetime, timedelta
from math import asin, cos, radians, sin, sqrt
from typing import Any, Callable


NO_ELIGIBLE_VENUES = "NO_ELIGIBLE_VENUES"
CLUSTER_RADIUS_KM = 1.5
MAX_CLUSTERS = 3
FOOD_TYPES = {"restaurant", "food", "meal_takeaway", "cafe", "bakery", "bar"}
INTENSITY_COST = {"high": 3.0, "medium": 2.0, "low": 1.0}
PACE_BUDGET = {"relaxed": 15.0, "moderate": 22.0, "packed": 30.0}


TransitFn = Callable[..., dict[str, Any]]


def optimise_route(
    venues: list[dict[str, Any]],
    date: str,
    start_time: str,
    pace: str,
    group_profile: dict[str, Any],
    accommodation_coords: dict[str, float],
    transit_fn: TransitFn | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Create a deterministic day route from candidate venues.

    The implementation follows PRD 6.1 order: filter, radius cluster, order by opening,
    apply energy rules, assign times with injected transit, annotate peak overlap, and insert
    rest/dining-style breaks where needed. `transit_fn` is dependency-injected; no live APIs are
    called from this tool.
    """
    day_of_week = _day_of_week(date)
    eligible = _filter_venues(venues, day_of_week, group_profile)
    if not eligible:
        return {
            "error": {
                "code": NO_ELIGIBLE_VENUES,
                "message": f"No eligible venues remain after route filters for {date}.",
            }
        }

    clusters = _radius_cluster(
        eligible,
        radius_km=CLUSTER_RADIUS_KM,
        max_clusters=MAX_CLUSTERS,
        anchor=accommodation_coords,
    )
    clusters = sorted(clusters, key=lambda cluster: _earliest_open(cluster, day_of_week))

    ordered: list[dict[str, Any]] = []
    for cluster in clusters:
        ordered.extend(sorted(cluster, key=lambda venue: _venue_open(venue, day_of_week) or "23:59"))

    ordered = apply_energy_logic(ordered, pace, group_profile, date)
    _assign_times(ordered, day_of_week, start_time, group_profile, transit_fn)
    if _insert_energy_breather_if_needed(ordered, pace, group_profile, date):
        _assign_times(ordered, day_of_week, start_time, group_profile, transit_fn)
    _annotate_peak_overlap(ordered, day_of_week)
    if _insert_dining(ordered):
        _assign_times(ordered, day_of_week, start_time, group_profile, transit_fn)
        _annotate_peak_overlap(ordered, day_of_week)
    return ordered


def apply_energy_logic(
    ordered_venues: list[dict[str, Any]],
    pace: str,
    group_profile: dict[str, Any],
    date: str,
) -> list[dict[str, Any]]:
    """Apply deterministic energy-cost annotations and mandatory child rest blocks."""
    del pace, date  # Used by breather placement after times exist; keep public helper contract.
    ordered = [deepcopy(venue) for venue in ordered_venues]
    for venue in ordered:
        venue.setdefault("energy_cost", calculate_venue_energy_cost(venue, weather_data={}))
        venue.setdefault("reasoning", "")

    if any(member.get("age", 0) < 10 for member in group_profile.get("members", [])):
        ordered = _insert_rest_block(ordered, time="13:00", duration=60)

    return ordered


def calculate_venue_energy_cost(venue: dict[str, Any], weather_data: dict[str, Any]) -> float:
    """Each venue gets a simple 1-10 energy cost score from PRD factors."""
    cost = INTENSITY_COST.get(venue.get("physical_intensity"), 2.0)
    extra_30min_blocks = max(0, (venue.get("estimated_duration_minutes", 60) - 60) // 30)
    cost += extra_30min_blocks * 0.25
    if venue.get("outdoor", False) and weather_data.get("high_c", 0) > 28:
        cost += 0.5
    return round(min(10.0, max(1.0, cost)), 2)


def _filter_venues(
    venues: list[dict[str, Any]], day_of_week: str, group_profile: dict[str, Any]
) -> list[dict[str, Any]]:
    restrictions = [r.lower() for r in group_profile.get("dietary_restrictions", []) if r]
    mobility_max = group_profile.get("mobility_max", "full")
    return [
        deepcopy(venue)
        for venue in venues
        if _is_open_on(venue, day_of_week)
        and _is_dietary_compatible(venue, restrictions)
        and _is_mobility_compatible(venue, mobility_max)
    ]


def _is_open_on(venue: dict[str, Any], day_of_week: str) -> bool:
    hours = venue.get("opening_hours") or {}
    day_hours = hours.get(day_of_week) or {}
    return bool(day_hours.get("open") and day_hours.get("close"))


def _is_dietary_compatible(venue: dict[str, Any], restrictions: list[str]) -> bool:
    if not restrictions:
        return True
    is_food = bool(set(venue.get("types", [])).intersection(FOOD_TYPES)) or venue.get("dietary_relevance") == "high"
    if not is_food:
        return True
    supported = {diet.lower() for diet in venue.get("dietary_supported", [])}
    return set(restrictions).issubset(supported)


def _is_mobility_compatible(venue: dict[str, Any], mobility_max: str) -> bool:
    accessibility = venue.get("wheelchair_accessibility", "varies")
    intensity = venue.get("physical_intensity", "medium")
    if mobility_max == "wheelchair":
        return accessibility == "full"
    if mobility_max == "limited":
        return intensity != "high" and accessibility in {"full", "partial", "varies"}
    return True


def _radius_cluster(
    venues: list[dict[str, Any]], radius_km: float, max_clusters: int, anchor: dict[str, float]
) -> list[list[dict[str, Any]]]:
    venues_by_anchor = sorted(
        venues,
        key=lambda venue: (_distance_km(anchor, venue["coordinates"]), venue.get("name", "")),
    )
    clusters: list[list[dict[str, Any]]] = []
    overflow: list[dict[str, Any]] = []

    for venue in venues_by_anchor:
        matching = None
        for cluster in clusters:
            if any(_distance_km(venue["coordinates"], other["coordinates"]) <= radius_km for other in cluster):
                matching = cluster
                break
        if matching is not None:
            matching.append(venue)
        elif len(clusters) < max_clusters:
            clusters.append([venue])
        else:
            overflow.append(venue)

    for venue in overflow:
        nearest = min(
            clusters,
            key=lambda cluster: min(_distance_km(venue["coordinates"], other["coordinates"]) for other in cluster),
        )
        nearest.append(venue)
    return clusters


def _earliest_open(cluster: list[dict[str, Any]], day_of_week: str) -> str:
    return min((_venue_open(venue, day_of_week) or "23:59") for venue in cluster)


def _venue_open(venue: dict[str, Any], day_of_week: str) -> str | None:
    return ((venue.get("opening_hours") or {}).get(day_of_week) or {}).get("open")


def _assign_times(
    ordered: list[dict[str, Any]],
    day_of_week: str,
    start_time: str,
    group_profile: dict[str, Any],
    transit_fn: TransitFn | None,
) -> None:
    current = _parse_time(start_time)
    transit = transit_fn or _zero_transit

    visit_indexes = [index for index, item in enumerate(ordered) if item.get("type") not in {"rest", "breather"}]
    visit_lookup = {index: position for position, index in enumerate(visit_indexes)}

    for index, item in enumerate(ordered):
        item.pop("transit_to_next_minutes", None)
        item.pop("transit_mode", None)
        item.pop("group_transport_note", None)

        if item.get("type") == "rest":
            rest_start = _parse_time(item["scheduled_time"])
            if current < rest_start:
                current = rest_start
            item["arrival_time"] = _format_time(current)
            current = current + timedelta(minutes=item["duration_minutes"])
            item["departure_time"] = _format_time(current)
            continue

        if item.get("type") == "breather":
            item["arrival_time"] = _format_time(current)
            current = current + timedelta(minutes=item["duration_minutes"])
            item["departure_time"] = _format_time(current)
            continue

        open_t = _parse_time(_venue_open(item, day_of_week) or "23:59")
        if item.get("scheduled_time"):
            open_t = max(open_t, _parse_time(item["scheduled_time"]))
        if current < open_t:
            current = open_t
            _append_reasoning(item, f"Start adjusted to venue opening ({_format_time(open_t)}).")

        item["arrival_time"] = _format_time(current)
        current = current + timedelta(minutes=item.get("estimated_duration_minutes", 60))
        item["departure_time"] = _format_time(current)

        visit_position = visit_lookup[index]
        if visit_position < len(visit_indexes) - 1:
            next_item = ordered[visit_indexes[visit_position + 1]]
            transit_result = transit(
                origin=item["coordinates"],
                destination=next_item["coordinates"],
                departure_time=item["departure_time"],
                group_size=group_profile.get("size", len(group_profile.get("members", []))),
            )
            duration = transit_result.get("duration_minutes", 0)
            item["transit_to_next_minutes"] = duration
            item["transit_mode"] = transit_result.get("mode")
            if transit_result.get("group_transport_note"):
                item["group_transport_note"] = transit_result["group_transport_note"]
            current = current + timedelta(minutes=duration)


def _insert_energy_breather_if_needed(
    ordered: list[dict[str, Any]], pace: str, group_profile: dict[str, Any], date: str
) -> bool:
    budget = _energy_budget(pace, group_profile, date)
    running_cost = 0.0
    for index, item in enumerate(list(ordered)):
        if item.get("type") in {"rest", "breather"}:
            continue
        running_cost += float(item.get("energy_cost", 2.0))
        if running_cost > budget * 0.7 and _parse_time(item["departure_time"]) < _parse_time("15:00"):
            if index + 1 >= len(ordered) or ordered[index + 1].get("type") != "breather":
                ordered.insert(
                    index + 1,
                    {
                        "type": "breather",
                        "name": "Breather break",
                        "duration_minutes": 30,
                        "reasoning": "Built in a breather here — you'll have covered a lot of ground.",
                    },
                )
            _append_reasoning(item, "Built in a breather here — you'll have covered a lot of ground.")
            return True
    return False


def _energy_budget(pace: str, group_profile: dict[str, Any], date: str) -> float:
    budget = PACE_BUDGET.get(pace, PACE_BUDGET["moderate"])
    members = group_profile.get("members", [])
    if any(member.get("age", 0) >= 65 for member in members):
        budget *= 0.8
    if any(member.get("age", 0) < 10 for member in members):
        budget *= 0.85
    if group_profile.get("jet_lag_active") and not group_profile.get("jet_lag_override"):
        day_num = _day_number(date, group_profile.get("arrival_date", date))
        if day_num == 1:
            budget *= 0.6
        elif day_num == 2:
            budget *= 0.8
    return budget


def _insert_rest_block(ordered: list[dict[str, Any]], time: str, duration: int) -> list[dict[str, Any]]:
    return ordered + [
        {
            "type": "rest",
            "name": "Midday rest",
            "scheduled_time": time,
            "duration_minutes": duration,
            "reasoning": "Mandatory midday rest for children under 10.",
        }
    ]


def _annotate_peak_overlap(ordered: list[dict[str, Any]], day_of_week: str) -> None:
    for item in ordered:
        if item.get("type") in {"rest", "breather"}:
            continue
        peak = _peak_window(item, day_of_week)
        if peak and _times_overlap(item["arrival_time"], item["departure_time"], peak["start"], peak["end"]):
            _append_reasoning(
                item,
                f"Note: arrives during peak hours ({peak['start']}–{peak['end']}). Consider shifting earlier if possible.",
            )


def _insert_dining(ordered: list[dict[str, Any]]) -> bool:
    dining_candidates = [item for item in ordered if _is_food_venue(item)]
    if not dining_candidates:
        return False

    for item in dining_candidates:
        ordered.remove(item)

    dining_candidates.sort(key=lambda item: (_first_opening_time(item), item.get("name", "")))
    lunch = dining_candidates[0]
    _mark_meal(lunch, meal="lunch", scheduled_time="12:00", note="Inserted as lunch near midday.")
    _insert_before_first_arrival_at_or_after(ordered, lunch, "12:00")

    if len(dining_candidates) > 1:
        dinner = dining_candidates[-1]
        _mark_meal(dinner, meal="dinner", scheduled_time="17:30", note="Inserted as dinner near end-of-day.")
        ordered.append(dinner)
    return True


def _is_food_venue(item: dict[str, Any]) -> bool:
    if item.get("type") in {"rest", "breather"}:
        return False
    return bool(set(item.get("types", [])).intersection(FOOD_TYPES)) or item.get("dietary_relevance") == "high"


def _mark_meal(item: dict[str, Any], meal: str, scheduled_time: str, note: str) -> None:
    item["meal"] = meal
    item["scheduled_time"] = scheduled_time
    _append_reasoning(item, note)


def _insert_before_first_arrival_at_or_after(ordered: list[dict[str, Any]], item: dict[str, Any], target_time: str) -> None:
    target = _parse_time(target_time)
    for index, existing in enumerate(ordered):
        arrival = existing.get("arrival_time")
        if arrival and _parse_time(arrival) >= target:
            ordered.insert(index, item)
            return
    ordered.append(item)


def _first_opening_time(item: dict[str, Any]) -> str:
    openings = [hours.get("open") for hours in (item.get("opening_hours") or {}).values() if hours.get("open")]
    return min(openings) if openings else "23:59"


def _peak_window(venue: dict[str, Any], day_of_week: str) -> dict[str, str] | None:
    if day_of_week in {"saturday", "sunday"}:
        return venue.get("crowd_peak_weekend")
    return venue.get("crowd_peak_weekday")


def _times_overlap(start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
    return _parse_time(start_a) < _parse_time(end_b) and _parse_time(start_b) < _parse_time(end_a)


def _day_of_week(date: str) -> str:
    return date_type.fromisoformat(date).strftime("%A").lower()


def _day_number(route_date: str, arrival_date: str) -> int:
    return (date_type.fromisoformat(route_date) - date_type.fromisoformat(arrival_date)).days + 1


def _parse_time(value: str) -> datetime:
    return datetime.strptime(value, "%H:%M")


def _format_time(value: datetime) -> str:
    return value.strftime("%H:%M")


def _distance_km(a: dict[str, float], b: dict[str, float]) -> float:
    earth_radius_km = 6371.0
    lat1, lng1 = radians(a["lat"]), radians(a["lng"])
    lat2, lng2 = radians(b["lat"]), radians(b["lng"])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    haversine = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return 2 * earth_radius_km * asin(sqrt(haversine))


def _append_reasoning(item: dict[str, Any], note: str) -> None:
    existing = item.get("reasoning", "")
    item["reasoning"] = f"{existing} {note}".strip()


def _zero_transit(**_: Any) -> dict[str, Any]:
    return {"duration_minutes": 0, "mode": "walking"}
