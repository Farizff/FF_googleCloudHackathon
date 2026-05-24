from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db.client import get_database

router = APIRouter()


class FlightAttachRequest(BaseModel):
    flight_number: str
    airline_iata: str
    origin_iata: str
    destination_iata: str
    member_ids: list[str]
    departure_datetime: str | None = None
    arrival_datetime: str | None = None
    risk_score: float
    risk_tier: str
    option_tier: str
    live_status: str = "unknown"
    live_status_last_polled: str | None = None


def get_db() -> Any:
    return get_database()


@router.get("/trips/{trip_id}/flights")
def list_trip_flights_endpoint(trip_id: str, db: Any = Depends(get_db)) -> dict[str, Any]:
    itineraries = list(db.itineraries.find({"trip_id": trip_id}))
    flights = []
    for itinerary in itineraries:
        flights.extend(itinerary.get("flights", []))
    return {"trip_id": trip_id, "flights": flights, "total_found": len(flights)}


@router.post("/itineraries/{itinerary_id}/flights")
def attach_flight_endpoint(
    itinerary_id: str,
    request: FlightAttachRequest,
    db: Any = Depends(get_db),
) -> dict[str, Any]:
    itinerary = db.itineraries.find_one({"itinerary_id": itinerary_id})
    if itinerary is None:
        raise HTTPException(status_code=404, detail={"code": "ITINERARY_NOT_FOUND", "message": "Itinerary not found."})
    flight = request.model_dump()
    db.itineraries.update_one({"itinerary_id": itinerary_id}, {"$push": {"flights": flight}})
    return {"success": True, "itinerary_id": itinerary_id, "flight": flight}
