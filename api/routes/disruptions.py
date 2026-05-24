from datetime import UTC, datetime
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from agent.tools.apply_disruption import apply_disruption
from api.firebase_rtdb import FirebaseProviderNotConfigured, FirebasePublishError, FirebaseRtdbPublisher
from api.settings import get_settings


router = APIRouter()


class Coordinates(BaseModel):
    lat: float
    lng: float


class TriggerDisruptionRequest(BaseModel):
    itinerary_id: str
    event_type: str
    description: str
    affected_day_numbers: list[int]
    current_location: Coordinates


def get_db() -> Any:
    raise RuntimeError("MongoDB dependency is not configured.")


def get_search_venues_nearby_fn() -> Callable[..., list[dict[str, Any]]]:
    raise RuntimeError("Venue search dependency is not configured.")


def get_transit_time_fn() -> Callable[..., dict[str, Any]]:
    raise RuntimeError("Transit dependency is not configured.")


def get_rank_alternatives_fn() -> Callable[[list[dict[str, Any]], list[dict[str, Any]], int], list[dict[str, Any]]]:
    return lambda reachable, profiles, available_minutes: reachable[:3]


def get_firebase_broadcaster() -> FirebaseRtdbPublisher:
    settings = get_settings()
    return FirebaseRtdbPublisher(settings.firebase_database_url)


def get_now_fn() -> Callable[[], str]:
    return _utc_now_iso


@router.post("/trigger-disruption")
def trigger_disruption(
    request: TriggerDisruptionRequest,
    db: Any = Depends(get_db),
    search_venues_nearby_fn: Callable[..., list[dict[str, Any]]] = Depends(get_search_venues_nearby_fn),
    get_transit_time_fn: Callable[..., dict[str, Any]] = Depends(get_transit_time_fn),
    rank_alternatives_fn: Callable[[list[dict[str, Any]], list[dict[str, Any]], int], list[dict[str, Any]]] = Depends(get_rank_alternatives_fn),
    firebase_broadcaster: FirebaseRtdbPublisher = Depends(get_firebase_broadcaster),
    now_fn: Callable[[], str] = Depends(get_now_fn),
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
            detail={"code": "FIREBASE_PROVIDER_NOT_CONFIGURED", "message": "Firebase Realtime Database is not configured."},
        ) from exc
    except FirebasePublishError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "FIREBASE_PUBLISH_FAILED", "message": "Firebase Realtime Database publish failed."},
        ) from exc

    return {**result, "map_pins": _map_pins(alternatives)}


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
