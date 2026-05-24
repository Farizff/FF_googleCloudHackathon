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


class TripCreateSimpleRequest(BaseModel):
    """Minimal trip creation input for chat-driven flow."""
    user_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    destination_city: str = Field(min_length=1)
    destination_country: str = "Unknown"
    destination_iata: str = "SYD"
    departure_date: str | None = None
    return_date: str | None = None
    num_people: int | None = None
    occasion: str | None = None
    origin_city_iata: str | None = None


class TripJoinRequest(BaseModel):
    """Join a trip via invite token."""
    invite_token: str
    user_id: str
    name: str
    origin_city_iata: str | None = None


def get_db() -> Any:
    return get_database()


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_id_fn() -> Callable[[str], str]:
    return lambda prefix: f"{prefix}_{uuid4().hex}"


def get_now_fn() -> Callable[[], str]:
    return _utc_now_iso


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


@router.post("/simple")
def create_trip_simple_endpoint(
    request: TripCreateSimpleRequest,
    db: Any = Depends(get_db),
    id_fn: Callable[[str], str] = Depends(get_id_fn),
) -> dict[str, Any]:
    """Simplified trip creation from chat: minimal fields → full group_trips document."""
    now = _utc_now_iso()
    trip_id = id_fn("trip")

    # Determine group_type and trip_mode from context
    group_type = "friends"
    trip_mode = "international"

    trip = {
        "trip_id": trip_id,
        "created_at": now,
        "invite_token": id_fn("invite"),
        "group_type": group_type,
        "trip_mode": trip_mode,
        "status": "planning",
        "special_occasion": request.occasion,
        "destination_city": request.destination_city,
        "destination_country": request.destination_country,
        "destination_iata": request.destination_iata,
        "departure_date": request.departure_date,
        "return_date": request.return_date,
        "members": [
            {
                "user_id": request.user_id,
                "name": request.name,
                "role": "organiser",
                "origin_city_iata": request.origin_city_iata,
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
    return {"success": True, "trip_id": trip_id, "trip": trip}


@router.get("/{trip_id}")
def get_trip_endpoint(trip_id: str, db: Any = Depends(get_db)) -> dict[str, Any]:
    trip = db.group_trips.find_one({"trip_id": trip_id})
    if trip is None:
        raise HTTPException(status_code=404, detail={"code": "TRIP_NOT_FOUND", "message": "Trip not found."})
    return {"trip": trip}


@router.post("/join")
def join_trip_endpoint(
    request: TripJoinRequest,
    db: Any = Depends(get_db),
    id_fn: Callable[[str], str] = Depends(get_id_fn),
    now_fn: Callable[[], str] = Depends(get_now_fn),
) -> dict[str, Any]:
    """
    Allow a user to join a trip by presenting an invite_token.

    Looks up the invite_token in invite_tokens collection, verifies it's active,
    finds the associated trip, adds the member, and returns success with trip info.
    """
    invite = db.invite_tokens.find_one({"token": request.invite_token, "status": "active"})
    if invite is None:
        raise HTTPException(status_code=404, detail={"code": "INVITE_NOT_FOUND", "message": "Invite token not found or inactive."})

    trip_id = invite.get("trip_id")
    trip = db.group_trips.find_one({"trip_id": trip_id})
    if trip is None:
        raise HTTPException(status_code=404, detail={"code": "TRIP_NOT_FOUND", "message": "Trip not found."})

    # Check if user already a member
    for member in trip.get("members", []):
        if member.get("user_id") == request.user_id:
            raise HTTPException(status_code=409, detail={"code": "MEMBER_ALREADY_EXISTS", "message": "User is already in this trip."})

    role = invite.get("role", "member")
    now = now_fn()
    member = {
        "user_id": request.user_id,
        "name": request.name,
        "role": role,
        "origin_city_iata": request.origin_city_iata,
        "joined_at": now,
        "profile_complete": False,
        "shares_compliance_with_admins": True,
    }
    trip.setdefault("members", []).append(member)
    db.group_trips.update_one({"trip_id": trip_id}, {"$set": {"members": trip["members"]}})

    return {"success": True, "trip_id": trip_id, "trip_name": trip.get("destination_city", "Trip")}


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
