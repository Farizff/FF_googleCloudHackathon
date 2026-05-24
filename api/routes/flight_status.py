from datetime import UTC, datetime
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db.client import get_database

router = APIRouter(prefix="/flight-status")


class FlightStatusUpdateRequest(BaseModel):
    live_status: str
    status_note: str | None = None


def get_db() -> Any:
    return get_database()


def get_now_fn() -> Callable[[], str]:
    return _utc_now_iso


@router.patch("/{itinerary_id}/{flight_number}")
def update_flight_status_endpoint(
    itinerary_id: str,
    flight_number: str,
    request: FlightStatusUpdateRequest,
    db: Any = Depends(get_db),
    now_fn: Callable[[], str] = Depends(get_now_fn),
) -> dict[str, Any]:
    itinerary = db.itineraries.find_one({"itinerary_id": itinerary_id})
    if itinerary is None:
        raise HTTPException(status_code=404, detail={"code": "ITINERARY_NOT_FOUND", "message": "Itinerary not found."})

    matching_flight = None
    for flight in itinerary.get("flights", []):
        if flight.get("flight_number") == flight_number:
            matching_flight = flight
            break
    if matching_flight is None:
        raise HTTPException(status_code=404, detail={"code": "FLIGHT_NOT_FOUND", "message": "Flight not found."})

    timestamp = now_fn()
    matching_flight["live_status"] = request.live_status
    matching_flight["live_status_last_polled"] = timestamp
    event = {
        "itinerary_id": itinerary_id,
        "flight_number": flight_number,
        "live_status": request.live_status,
        "status_note": request.status_note,
        "created_at": timestamp,
    }
    db.flight_status_events.insert_one(event)
    db.itineraries.update_one({"itinerary_id": itinerary_id}, {"$set": {"flights": itinerary.get("flights", [])}})
    return {"success": True, "itinerary_id": itinerary_id, "flight_number": flight_number, "live_status": request.live_status}


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
