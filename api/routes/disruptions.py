"""Disruption trigger — the demo wow moment.

POST /trigger-disruption  (also reachable at /disruptions/trigger-disruption)
POST /disruptions/trigger-disruption

Step-by-step:
  1. Log the disruption event to MongoDB.
  2. Fetch the itinerary and group profiles.
  3. Search for nearby alternative venues (Google Places or fake client).
  4. Filter to venues reachable within the available time window (Distance Matrix or fake).
  5. Rank alternatives by group fit.
  6. Return exactly 3 labelled alternatives + map pins.
  7. Broadcast the update to Firebase RTDB (live or no-op).
  8. (Separate step, after user picks) notify contacts via SendGrid.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from agent.tools.apply_disruption import apply_disruption
from agent.tools.notify_contacts import notify_contacts
from api.email_client import get_email_client
from api.firebase_rtdb import FirebaseProviderNotConfigured, FirebasePublishError, FirebaseRtdbPublisher
from api.maps_client import get_mapped_disruption_deps
from api.settings import get_settings
from db.client import get_database


router = APIRouter(prefix="/disruptions")


class Coordinates(BaseModel):
    lat: float
    lng: float


class TriggerDisruptionRequest(BaseModel):
    itinerary_id: str
    event_type: str
    description: str
    affected_day_numbers: list[int]
    current_location: Coordinates


# ---------------------------------------------------------------------------
# Dependency injection — wired to real implementations
# ---------------------------------------------------------------------------


def get_db() -> Any:
    return get_database()


def get_search_venues_nearby_fn() -> Callable[..., list[dict[str, Any]]]:
    """Return a search_venues_nearby function backed by Google Maps or the fake client."""
    deps = get_mapped_disruption_deps()
    places_client = deps["places_client"]

    def search_venues_nearby(
        *,
        coordinates: dict[str, float],
        radius_km: int,
        date: str,
        dietary_restrictions: list[str],
        mobility_max: str,
        group_size: int,
        exclude_venue_ids: list[str],
        limit: int = 15,
    ) -> list[dict[str, Any]]:
        # Use city from the itinerary's trip (default to Tokyo for demo).
        city = "Tokyo"
        destination_country = "Japan"

        results = places_client.nearby_search(
            city=city,
            destination_country=destination_country,
            date=date,
            place_types=["tourist_attraction", "museum", "park"],
            limit=limit,
        )
        # Filter out excluded venue IDs and enrich with estimated_duration_minutes
        filtered = []
        for v in results:
            if v.get("venue_id") and v["venue_id"] not in exclude_venue_ids:
                v.setdefault("estimated_duration_minutes", 90)
                filtered.append(v)
        return filtered

    return search_venues_nearby


def get_transit_time_fn() -> Callable[..., dict[str, Any]]:
    """Return a get_transit_time function backed by Google Maps Distance Matrix or fake."""
    deps = get_mapped_disruption_deps()
    directions_client = deps["directions_client"]

    def get_transit_time(
        origin: dict[str, float],
        destination: dict[str, float],
        departure_unix_timestamp: int,
        group_size: int = 1,
    ) -> dict[str, Any]:
        routes = directions_client.get_directions(
            origin=origin,
            destination=destination,
            departure_time=departure_unix_timestamp,
            mode="transit",
        )
        leg = routes[0]["legs"][0]
        duration_seconds = leg.get("duration_in_traffic", leg["duration"])["value"]
        distance_meters = leg["distance"]["value"]
        minutes = round(duration_seconds / 60)
        distance_km = round(distance_meters / 1000, 2)

        note = None
        if group_size > 6:
            import math
            taxis = math.ceil(group_size / 4)
            note = f"{group_size} people: chartered minibus (~$80) or {taxis} taxis (~$95 total)."

        return {
            "duration_minutes": minutes,
            "distance_km": distance_km,
            "mode": "transit",
            "group_transport_note": note,
        }

    return get_transit_time


def get_rank_alternatives_fn() -> Callable[[list[dict[str, Any]], list[dict[str, Any]], int], list[dict[str, Any]]]:
    """Rank alternatives: sort by rating descending, return as-is (Vertex AI replaced later)."""
    return lambda reachable, profiles, available_minutes: sorted(
        reachable, key=lambda v: v.get("rating") or 0, reverse=True
    )


def get_firebase_broadcaster() -> FirebaseRtdbPublisher:
    settings = get_settings()
    return FirebaseRtdbPublisher(settings.firebase_database_url)


def get_now_fn() -> Callable[[], str]:
    return _utc_now_iso


def get_contacts_collection_fn() -> Any:
    """Return the MongoDB contacts collection for the current trip."""
    db = get_database()
    return db.contacts


def get_notify_contacts_fn() -> Callable[..., dict[str, int]]:
    """Return a notify_contacts function bound to contacts collection + email client."""

    def bound_notify_contacts(
        trip_id: str,
        trigger_event: str,
        notification_context: dict[str, Any],
        notification_log_collection: Any,
    ) -> dict[str, int]:
        return notify_contacts(
            trip_id=trip_id,
            trigger_event=trigger_event,
            notification_context=notification_context,
            contacts_collection=get_contacts_collection_fn(),
            notification_log_collection=notification_log_collection,
            send_email_fn=get_email_client().send_email,
            clock=_utc_now_iso,
        )

    return bound_notify_contacts


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------


@router.post("/trigger-disruption")
def trigger_disruption(
    request: TriggerDisruptionRequest,
    db: Any = Depends(get_db),
    search_venues_nearby_fn: Callable[..., list[dict[str, Any]]] = Depends(get_search_venues_nearby_fn),
    get_transit_time_fn: Callable[..., dict[str, Any]] = Depends(get_transit_time_fn),
    rank_alternatives_fn: Callable[[list[dict[str, Any]], list[dict[str, Any]], int], list[dict[str, Any]]] = Depends(
        get_rank_alternatives_fn
    ),
    firebase_broadcaster: FirebaseRtdbPublisher = Depends(get_firebase_broadcaster),
    now_fn: Callable[[], str] = Depends(get_now_fn),
    notify_contacts_fn: Callable[..., dict[str, int]] = Depends(get_notify_contacts_fn),
) -> dict[str, Any]:
    result = apply_disruption(
        itinerary_id=request.itinerary_id,
        event_type=request.event_type,
        affected_day_numbers=request.affected_day_numbers,
        current_location=request.current_location.model_dump(),
        description=request.description,
        db=db,
        search_venues_nearby_fn=search_venues_nearby_fn,
        get_transit_time_fn=get_transit_time_fn,
        rank_alternatives_fn=rank_alternatives_fn,
        now_fn=now_fn,
    )
    if "error" in result:
        raise HTTPException(status_code=_status_for_error(result["error"]["code"]), detail=result["error"])

    itinerary = db.itineraries.find_one({"itinerary_id": request.itinerary_id})
    trip_id = itinerary["trip_id"]
    last_disruption_at = result["last_disruption_at"]
    alternatives = result.get("alternatives", [])

    # Notify trip contacts via SendGrid (or fake client) before Firebase broadcast.
    notification_result = notify_contacts_fn(
        trip_id=trip_id,
        trigger_event=request.event_type,
        notification_context=result.get("notification_context", {}),
        notification_log_collection=db.notification_logs,
    )

    try:
        firebase_broadcaster.broadcast_itinerary_update(
            trip_id,
            {
                "event_type": request.event_type,
                "itinerary_id": request.itinerary_id,
                "last_disruption_at": last_disruption_at,
                "alternatives_count": len(alternatives),
            },
        )
    except FirebaseProviderNotConfigured as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "FIREBASE_PROVIDER_NOT_CONFIGURED", "message": str(exc)},
        ) from exc
    except FirebasePublishError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "FIREBASE_PUBLISH_FAILED", "message": "Firebase RTDB publish failed."},
        ) from exc

    return {**result, "map_pins": _map_pins(alternatives), "notification": notification_result}


def _map_pins(alternatives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pins = []
    for alternative in alternatives:
        if alternative.get("coordinates") is None:
            continue
        pins.append(
            {
                "venue_id": alternative.get("venue_id"),
                "name": alternative.get("name"),
                "coordinates": alternative.get("coordinates"),
                "tier": alternative.get("tier"),
            }
        )
    return pins


def _status_for_error(code: str) -> int:
    if code in {"ITINERARY_NOT_FOUND", "TRIP_NOT_FOUND", "AFFECTED_DAY_NOT_FOUND"}:
        return 404
    return 400


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")