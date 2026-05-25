from datetime import UTC, datetime
from typing import Any, Callable
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db.client import get_database

router = APIRouter(prefix="/itineraries")


class ItineraryCreateRequest(BaseModel):
    trip_id: str
    days: list[dict[str, Any]] = []
    accommodation: dict[str, Any] | None = None


class StatusUpdateRequest(BaseModel):
    status: str


def get_db() -> Any:
    return get_database()


def get_id_fn() -> Callable[[str], str]:
    return lambda prefix: f"{prefix}_{uuid4().hex}"


@router.post("")
def create_itinerary_endpoint(
    request: ItineraryCreateRequest,
    db: Any = Depends(get_db),
    id_fn: Callable[[str], str] = Depends(get_id_fn),
) -> dict[str, Any]:
    if db.group_trips.find_one({"trip_id": request.trip_id}) is None:
        raise HTTPException(status_code=404, detail={"code": "TRIP_NOT_FOUND", "message": "Trip not found."})
    now = _utc_now_iso()
    itinerary = {
        "itinerary_id": id_fn("itinerary"),
        "trip_id": request.trip_id,
        "created_at": now,
        "updated_at": now,
        "status": "draft",
        "accommodation": request.accommodation,
        "days": request.days,
        "flights": [],
        "disruption_log": [],
        "share_url_token": id_fn("share"),
    }
    db.itineraries.insert_one(itinerary)
    return {"success": True, "itinerary": itinerary}


@router.get("/{itinerary_id}")
def get_itinerary_endpoint(itinerary_id: str, db: Any = Depends(get_db)) -> dict[str, Any]:
    itinerary = _get_itinerary_or_404(db, itinerary_id)
    itinerary.pop("_id", None)
    return {"itinerary": itinerary}


@router.patch("/{itinerary_id}/status")
def update_itinerary_status_endpoint(
    itinerary_id: str,
    request: StatusUpdateRequest,
    db: Any = Depends(get_db),
) -> dict[str, Any]:
    itinerary = _get_itinerary_or_404(db, itinerary_id)
    itinerary["status"] = request.status
    itinerary["updated_at"] = _utc_now_iso()
    db.itineraries.update_one({"itinerary_id": itinerary_id}, {"$set": {"status": request.status, "updated_at": itinerary["updated_at"]}})
    return {"success": True, "itinerary_id": itinerary_id, "status": request.status}


def _get_itinerary_or_404(db: Any, itinerary_id: str) -> dict[str, Any]:
    itinerary = db.itineraries.find_one({"itinerary_id": itinerary_id})
    if itinerary is None:
        raise HTTPException(status_code=404, detail={"code": "ITINERARY_NOT_FOUND", "message": "Itinerary not found."})
    return itinerary


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
