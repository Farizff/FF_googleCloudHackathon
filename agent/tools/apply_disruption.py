from datetime import UTC, datetime
from typing import Any, Callable


ITINERARY_NOT_FOUND = "ITINERARY_NOT_FOUND"
TRIP_NOT_FOUND = "TRIP_NOT_FOUND"
AFFECTED_DAY_NOT_FOUND = "AFFECTED_DAY_NOT_FOUND"
OPTION_TIERS = ["budget", "recommended", "premium"]
MOBILITY_ORDER = {"full": 0, "limited": 1, "wheelchair": 2}


def apply_disruption(
    itinerary_id: str,
    event_type: str,
    affected_day_numbers: list[int],
    current_location: dict[str, float],
    description: str,
    db: Any,
    search_venues_nearby_fn: Callable[..., list[dict[str, Any]]],
    get_transit_time_fn: Callable[..., dict[str, Any]],
    rank_alternatives_fn: Callable[[list[dict[str, Any]], list[dict[str, Any]], int], list[dict[str, Any]]],
    now_fn: Callable[[], str] | None = None,
) -> dict[str, Any]:
    """Build reachable disruption alternatives using injected data/tool dependencies."""
    now = now_fn or _utc_now_iso
    itinerary = db.itineraries.find_one({"itinerary_id": itinerary_id})
    if itinerary is None:
        return _error(ITINERARY_NOT_FOUND, f"Itinerary not found for itinerary_id '{itinerary_id}'.")

    affected_day = _find_affected_day(itinerary, affected_day_numbers)
    if affected_day is None:
        return _error(
            AFFECTED_DAY_NOT_FOUND,
            f"No affected day found for day numbers {affected_day_numbers} in itinerary '{itinerary_id}'.",
        )

    trip = db.group_trips.find_one({"trip_id": itinerary["trip_id"]})
    if trip is None:
        return _error(TRIP_NOT_FOUND, f"Trip not found for trip_id '{itinerary['trip_id']}'.")

    created_at = now()
    db.disruption_events.insert_one(
        {
            "itinerary_id": itinerary_id,
            "event_type": event_type,
            "description": description,
            "created_at": created_at,
        }
    )

    profiles = _get_group_profiles(db, trip.get("members", []))
    available_minutes = _calculate_window_minutes(affected_day, event_type)
    scheduled_venue_ids = [
        stop["venue_id"] for stop in affected_day.get("shared_schedule", []) if stop.get("venue_id")
    ]

    candidates = search_venues_nearby_fn(
        coordinates=current_location,
        radius_km=3,
        date=affected_day["date"],
        dietary_restrictions=_aggregate_dietary(profiles),
        mobility_max=_max_mobility(profiles),
        group_size=len(trip.get("members", [])),
        exclude_venue_ids=scheduled_venue_ids,
        limit=15,
    )

    reachable = _filter_reachable_candidates(
        candidates=candidates,
        current_location=current_location,
        departure_unix_timestamp=_iso_to_unix(created_at),
        group_size=len(trip.get("members", [])),
        available_minutes=available_minutes,
        get_transit_time_fn=get_transit_time_fn,
    )
    ranked = rank_alternatives_fn(reachable, profiles, available_minutes)

    return {
        "alternatives": _label_three_options(ranked),
        "available_window_minutes": available_minutes,
        "notification_context": {
            "event_description": description,
            "changes_summary": "Day rebuilt with alternatives near current location.",
        },
    }


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _error(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


def _find_affected_day(itinerary: dict[str, Any], day_numbers: list[int]) -> dict[str, Any] | None:
    requested = set(day_numbers)
    for day in itinerary.get("days", []):
        if day.get("day_number") in requested:
            return day
    return None


def _get_group_profiles(db: Any, member_ids: list[str]) -> list[dict[str, Any]]:
    profiles = []
    for user_id in member_ids:
        profile = db.traveller_profiles.find_one({"user_id": user_id})
        if profile is not None:
            profiles.append(profile)
    return profiles


def _aggregate_dietary(profiles: list[dict[str, Any]]) -> list[str]:
    restrictions: list[str] = []
    seen = set()
    for profile in profiles:
        values = profile.get("dietary_restrictions") or profile.get("dietary") or []
        for value in values:
            key = str(value).lower()
            if key and key not in seen:
                seen.add(key)
                restrictions.append(key)
    return restrictions


def _max_mobility(profiles: list[dict[str, Any]]) -> str:
    max_value = "full"
    for profile in profiles:
        mobility = profile.get("mobility") or profile.get("mobility_max") or "full"
        if MOBILITY_ORDER.get(mobility, 0) > MOBILITY_ORDER[max_value]:
            max_value = mobility
    return max_value


def _calculate_window_minutes(day: dict[str, Any], event_type: str) -> int:
    """Return available replacement window between first disrupted stop and next commitment."""
    del event_type  # Reserved for future event-specific window rules.
    schedule = day.get("shared_schedule", [])
    if not schedule:
        return 0
    first_stop = schedule[0]
    window_start = _parse_hhmm(first_stop.get("arrival_time", "00:00"))
    if len(schedule) > 1:
        window_end = _parse_hhmm(schedule[1].get("arrival_time", "23:59"))
    else:
        window_end = _parse_hhmm(first_stop.get("departure_time", "23:59"))
    return max(0, window_end - window_start)


def _parse_hhmm(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def _iso_to_unix(value: str) -> int:
    normalized = value.replace("Z", "+00:00")
    return int(datetime.fromisoformat(normalized).timestamp())


def _filter_reachable_candidates(
    candidates: list[dict[str, Any]],
    current_location: dict[str, float],
    departure_unix_timestamp: int,
    group_size: int,
    available_minutes: int,
    get_transit_time_fn: Callable[..., dict[str, Any]],
) -> list[dict[str, Any]]:
    reachable = []
    for candidate in candidates:
        transit = get_transit_time_fn(
            current_location,
            candidate["coordinates"],
            departure_unix_timestamp,
            group_size=group_size,
        )
        total_minutes = (
            transit["duration_minutes"] + candidate.get("estimated_duration_minutes", 0) + 30
        )
        if total_minutes < available_minutes:
            enriched = {
                **candidate,
                "transit_minutes_from_disruption": transit["duration_minutes"],
                "transit_mode_from_disruption": transit.get("mode"),
            }
            if transit.get("group_transport_note"):
                enriched["group_transport_note"] = transit["group_transport_note"]
            reachable.append(enriched)
    return reachable


def _label_three_options(ranked: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labelled = []
    for tier, candidate in zip(OPTION_TIERS, ranked[:3]):
        labelled.append({**candidate, "tier": tier})
    return labelled
