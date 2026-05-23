from datetime import datetime
from typing import Any, Callable


CACHE_WINDOW_MINUTES = 30
FLIGHT_STATUS_CHANGE_TOPIC = "flight-status-change"
OUTPUT_FIELDS = [
    "status",
    "scheduled_departure",
    "actual_departure",
    "scheduled_arrival",
    "actual_arrival",
    "delay_minutes",
]


def poll_flight_status(
    flight_number: str,
    departure_date: str,
    cache_collection: Any,
    aerodatabox_client: Any,
    pubsub_publisher: Any,
    clock: Callable[[], str] | None = None,
) -> dict[str, Any]:
    """Poll live flight status with a 30-minute MongoDB cache and Pub/Sub change events."""
    now_iso = (clock or _utc_now_iso)()
    query = {"flight_number": flight_number, "departure_date": departure_date}
    cached = cache_collection.find_one(query)

    if cached is not None and _is_cache_fresh(cached.get("polled_at"), now_iso):
        return _public_status(cached)

    live_status = _normalize_status(
        aerodatabox_client.get_flight_by_number(flight_number, departure_date)
    )
    cache_document = {
        "flight_number": flight_number,
        "departure_date": departure_date,
        "polled_at": now_iso,
        **live_status,
    }
    cache_collection.replace_one(query, cache_document, upsert=True)

    if cached is not None and cached.get("status") != live_status.get("status"):
        pubsub_publisher.publish(
            FLIGHT_STATUS_CHANGE_TOPIC,
            {
                "flight_number": flight_number,
                "departure_date": departure_date,
                "previous_status": cached.get("status"),
                "status": live_status.get("status"),
                "delay_minutes": live_status.get("delay_minutes"),
            },
        )

    return live_status


def _utc_now_iso() -> str:
    # Keep import surface small; most callers inject clock in tests and scheduled jobs.
    from datetime import UTC

    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _is_cache_fresh(polled_at: Any, now_iso: str) -> bool:
    polled = _parse_datetime(polled_at)
    now = _parse_datetime(now_iso)
    if polled is None or now is None:
        return False
    age_seconds = (now - polled).total_seconds()
    return 0 <= age_seconds < CACHE_WINDOW_MINUTES * 60


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _public_status(document: dict[str, Any]) -> dict[str, Any]:
    return {field: document.get(field) for field in OUTPUT_FIELDS}


def _normalize_status(response: Any) -> dict[str, Any]:
    flight = _first_flight(response)
    if _already_normalized(flight):
        return _public_status(flight)

    departure = flight.get("departure") or {}
    arrival = flight.get("arrival") or {}
    return {
        "status": str(flight.get("status") or "unknown").lower(),
        "scheduled_departure": _nested_time(departure, "scheduledTime"),
        "actual_departure": _nested_time(departure, "actualTime"),
        "scheduled_arrival": _nested_time(arrival, "scheduledTime"),
        "actual_arrival": _nested_time(arrival, "actualTime"),
        "delay_minutes": int(departure.get("delayMinutes") or arrival.get("delayMinutes") or 0),
    }


def _first_flight(response: Any) -> dict[str, Any]:
    if isinstance(response, list):
        return response[0] if response else {}
    if isinstance(response, dict) and isinstance(response.get("flights"), list):
        return response["flights"][0] if response["flights"] else {}
    if isinstance(response, dict):
        return response
    return {}


def _already_normalized(flight: dict[str, Any]) -> bool:
    return all(field in flight for field in OUTPUT_FIELDS)


def _nested_time(section: dict[str, Any], field: str) -> str | None:
    value = section.get(field)
    if isinstance(value, dict):
        return value.get("local") or value.get("utc")
    if isinstance(value, str):
        return value
    return None
