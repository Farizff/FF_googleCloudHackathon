from math import ceil
from typing import Any


TAXI_CAPACITY = 4
LARGE_GROUP_THRESHOLD = 6


def get_transit_time(
    origin: dict[str, float],
    destination: dict[str, float],
    departure_unix_timestamp: int,
    mode: str,
    group_size: int,
    directions_client: Any,
) -> dict[str, Any]:
    """Estimate point-to-point travel time using an injected directions client."""
    routes = directions_client.get_directions(
        origin=origin,
        destination=destination,
        departure_time=departure_unix_timestamp,
        mode=mode,
    )
    leg = routes[0]["legs"][0]

    duration_seconds = leg.get("duration_in_traffic", leg["duration"])["value"]
    distance_meters = leg["distance"]["value"]

    return {
        "duration_minutes": round(duration_seconds / 60),
        "distance_km": round(distance_meters / 1000, 2),
        "mode": mode,
        "group_transport_note": _group_transport_note(group_size),
    }


def _group_transport_note(group_size: int) -> str | None:
    if group_size <= LARGE_GROUP_THRESHOLD:
        return None

    taxi_count = ceil(group_size / TAXI_CAPACITY)
    return f"{group_size} people: chartered minibus (~$80) or {taxi_count} taxis (~$95 total)."
