from datetime import UTC, datetime
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db.client import get_database

router = APIRouter(prefix="/trips")


class MemberAddRequest(BaseModel):
    user_id: str
    name: str
    role: str = "member"
    origin_city_iata: str | None = None


class RoleUpdateRequest(BaseModel):
    role: str
    actor_user_id: str


def get_db() -> Any:
    return get_database()


def get_now_fn() -> Callable[[], str]:
    return _utc_now_iso


@router.post("/{trip_id}/members")
def add_member_endpoint(
    trip_id: str,
    request: MemberAddRequest,
    db: Any = Depends(get_db),
    now_fn: Callable[[], str] = Depends(get_now_fn),
) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    member = {
        "user_id": request.user_id,
        "name": request.name,
        "role": request.role,
        "origin_city_iata": request.origin_city_iata,
        "joined_at": now_fn(),
        "profile_complete": False,
        "shares_compliance_with_admins": True,
    }
    trip.setdefault("members", []).append(member)
    db.group_trips.update_one({"trip_id": trip_id}, {"$set": {"members": trip["members"]}})
    return {"success": True, "trip_id": trip_id, "member": member}


@router.patch("/{trip_id}/members/{user_id}/role")
def update_member_role_endpoint(
    trip_id: str,
    user_id: str,
    request: RoleUpdateRequest,
    db: Any = Depends(get_db),
) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    actor = _find_member(trip, request.actor_user_id)
    target = _find_member(trip, user_id)
    if actor is None or target is None:
        raise HTTPException(status_code=404, detail={"code": "MEMBER_NOT_FOUND", "message": "Member not found."})
    if target.get("role") == "organiser" and request.role != "organiser":
        raise HTTPException(
            status_code=403,
            detail={"code": "ORGANISER_ROLE_LOCKED", "message": "The organiser cannot be demoted or removed by another member."},
        )
    if actor.get("role") not in {"organiser", "co_leader"}:
        raise HTTPException(status_code=403, detail={"code": "ROLE_UPDATE_FORBIDDEN", "message": "Only organisers or co-leaders can update roles."})
    target["role"] = request.role
    db.group_trips.update_one({"trip_id": trip_id}, {"$set": {"members": trip.get("members", [])}})
    return {"success": True, "trip_id": trip_id, "member": target}


def _get_trip_or_404(db: Any, trip_id: str) -> dict[str, Any]:
    trip = db.group_trips.find_one({"trip_id": trip_id})
    if trip is None:
        raise HTTPException(status_code=404, detail={"code": "TRIP_NOT_FOUND", "message": "Trip not found."})
    return trip


def _find_member(trip: dict[str, Any], user_id: str) -> dict[str, Any] | None:
    for member in trip.get("members", []):
        if member.get("user_id") == user_id:
            return member
    return None


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
