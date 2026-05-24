from datetime import UTC, datetime
from typing import Any, Callable
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from db.client import get_database

router = APIRouter(prefix="/trips")


class OrganiserInput(BaseModel):
    user_id: str
    name: str
    origin_city_iata: str | None = None


class TripCreateRequest(BaseModel):
    group_type: str
    trip_mode: str
    destination_city: str
    destination_country: str
    destination_iata: str
    organiser: OrganiserInput
    special_occasion: str | None = None


def get_db() -> Any:
    return get_database()


def get_id_fn() -> Callable[[str], str]:
    return lambda prefix: f"{prefix}_{uuid4().hex}"


@router.post("")
def create_trip_endpoint(
    request: TripCreateRequest,
    db: Any = Depends(get_db),
    id_fn: Callable[[str], str] = Depends(get_id_fn),
) -> dict[str, Any]:
    trip_id = id_fn("trip")
    now = _utc_now_iso()
    trip = {
        "trip_id": trip_id,
        "created_at": now,
        "invite_token": id_fn("invite"),
        "group_type": request.group_type,
        "trip_mode": request.trip_mode,
        "status": "planning",
        "special_occasion": request.special_occasion,
        "destination_city": request.destination_city,
        "destination_country": request.destination_country,
        "destination_iata": request.destination_iata,
        "members": [
            {
                "user_id": request.organiser.user_id,
                "name": request.organiser.name,
                "role": "organiser",
                "origin_city_iata": request.organiser.origin_city_iata,
                "joined_at": now,
                "profile_complete": False,
                "shares_compliance_with_admins": True,
            }
        ],
        "contacts": [],
        "office_details": {"company_name": None, "cost_centre": None},
        "shared_budget_estimate_usd": 0,
        "all_members_budget_ok": False,
        "jet_lag_override": False,
    }
    db.group_trips.insert_one(trip)
    return {"success": True, "trip": trip}


@router.get("/{trip_id}")
def get_trip_endpoint(trip_id: str, db: Any = Depends(get_db)) -> dict[str, Any]:
    trip = db.group_trips.find_one({"trip_id": trip_id})
    if trip is None:
        raise HTTPException(status_code=404, detail={"code": "TRIP_NOT_FOUND", "message": "Trip not found."})
    return {"trip": trip}


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
