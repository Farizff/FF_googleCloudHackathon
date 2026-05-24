from datetime import UTC, datetime
from typing import Any, Callable
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db.client import get_database

router = APIRouter(prefix="/trips")
MAX_CO_LEADERS = 2
ADMIN_ROLES = {"organiser", "co_leader"}


class MemberAddRequest(BaseModel):
    user_id: str
    name: str
    role: str = "member"
    origin_city_iata: str | None = None


class RoleUpdateRequest(BaseModel):
    role: str
    actor_user_id: str


class InviteCreateRequest(BaseModel):
    actor_user_id: str
    role: str = "member"


class InviteAcceptRequest(BaseModel):
    user_id: str
    name: str
    origin_city_iata: str | None = None


class SuggestionCreateRequest(BaseModel):
    submitted_by_user_id: str
    target_scope: str
    message: str
    flock_id: str | None = None
    supporter_user_ids: list[str] = []


class SuggestionReviewRequest(BaseModel):
    actor_user_id: str
    status: str
    admin_note: str | None = None


class FlockModeStartRequest(BaseModel):
    actor_user_id: str
    start_time: str


class FlockModeEndRequest(BaseModel):
    actor_user_id: str
    end_time: str


class FlockCreateRequest(BaseModel):
    actor_user_id: str
    flock_name: str
    flock_leader_user_id: str
    member_ids: list[str]
    schedule: list[dict[str, Any]] = []
    reconvene_time: str
    reconvene_location: str
    reconvene_coordinates: dict[str, float] | None = None


class FlockUpdateRequest(BaseModel):
    actor_user_id: str
    flock_name: str | None = None
    flock_leader_user_id: str | None = None
    member_ids: list[str] | None = None
    schedule: list[dict[str, Any]] | None = None
    reconvene_time: str | None = None
    reconvene_location: str | None = None
    reconvene_coordinates: dict[str, float] | None = None


class ActorRequest(BaseModel):
    actor_user_id: str


def get_db() -> Any:
    return get_database()


def get_now_fn() -> Callable[[], str]:
    return _utc_now_iso


def get_id_fn() -> Callable[[str], str]:
    return lambda prefix: f"{prefix}_{uuid4().hex[:12]}"


@router.post("/{trip_id}/members")
def add_member_endpoint(
    trip_id: str,
    request: MemberAddRequest,
    db: Any = Depends(get_db),
    now_fn: Callable[[], str] = Depends(get_now_fn),
) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    if request.role == "co_leader" and _co_leader_count(trip) >= MAX_CO_LEADERS:
        raise HTTPException(status_code=403, detail={"code": "CO_LEADER_LIMIT_REACHED", "message": "A trip can have at most two co-leaders."})
    member = _member_document(request.user_id, request.name, request.role, request.origin_city_iata, now_fn())
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
    if actor.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail={"code": "ROLE_UPDATE_FORBIDDEN", "message": "Only organisers or co-leaders can update roles."})
    if request.role == "co_leader" and target.get("role") != "co_leader" and _co_leader_count(trip) >= MAX_CO_LEADERS:
        raise HTTPException(status_code=403, detail={"code": "CO_LEADER_LIMIT_REACHED", "message": "A trip can have at most two co-leaders."})
    target["role"] = request.role
    db.group_trips.update_one({"trip_id": trip_id}, {"$set": {"members": trip.get("members", [])}})
    return {"success": True, "trip_id": trip_id, "member": target}


@router.post("/{trip_id}/invites")
def create_invite_endpoint(
    trip_id: str,
    request: InviteCreateRequest,
    db: Any = Depends(get_db),
    now_fn: Callable[[], str] = Depends(get_now_fn),
    id_fn: Callable[[str], str] = Depends(get_id_fn),
) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    actor = _require_member(trip, request.actor_user_id)
    if actor.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail={"code": "INVITE_FORBIDDEN", "message": "Only organisers or co-leaders can create invites."})
    if request.role == "co_leader" and _co_leader_count(trip) >= MAX_CO_LEADERS:
        raise HTTPException(status_code=403, detail={"code": "CO_LEADER_LIMIT_REACHED", "message": "A trip can have at most two co-leaders."})
    invite = {
        "token": id_fn("invite"),
        "trip_id": trip_id,
        "role": request.role,
        "created_by_user_id": request.actor_user_id,
        "created_at": now_fn(),
        "status": "active",
        "share_path": f"/trips/{trip_id}/invite",
    }
    db.invite_tokens.insert_one(invite)
    db.group_trips.update_one({"trip_id": trip_id}, {"$set": {"invite_token": invite["token"]}})
    return {"success": True, "invite": invite}


@router.post("/{trip_id}/invites/{token}/accept")
def accept_invite_endpoint(
    trip_id: str,
    token: str,
    request: InviteAcceptRequest,
    db: Any = Depends(get_db),
    now_fn: Callable[[], str] = Depends(get_now_fn),
) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    invite = db.invite_tokens.find_one({"trip_id": trip_id, "token": token})
    if invite is None or invite.get("status") != "active":
        raise HTTPException(status_code=404, detail={"code": "INVITE_NOT_FOUND", "message": "Invite token is not active."})
    if _find_member(trip, request.user_id) is not None:
        raise HTTPException(status_code=409, detail={"code": "MEMBER_ALREADY_EXISTS", "message": "User is already in this trip."})
    if invite.get("role") == "co_leader" and _co_leader_count(trip) >= MAX_CO_LEADERS:
        raise HTTPException(status_code=403, detail={"code": "CO_LEADER_LIMIT_REACHED", "message": "A trip can have at most two co-leaders."})
    member = _member_document(request.user_id, request.name, invite.get("role", "member"), request.origin_city_iata, now_fn())
    trip.setdefault("members", []).append(member)
    db.group_trips.update_one({"trip_id": trip_id}, {"$set": {"members": trip["members"]}})
    return {"success": True, "trip_id": trip_id, "member": member}


@router.post("/{trip_id}/suggestions")
def create_suggestion_endpoint(
    trip_id: str,
    request: SuggestionCreateRequest,
    db: Any = Depends(get_db),
    now_fn: Callable[[], str] = Depends(get_now_fn),
    id_fn: Callable[[str], str] = Depends(get_id_fn),
) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    _require_member(trip, request.submitted_by_user_id)
    suggestion = {
        "suggestion_id": id_fn("suggestion"),
        "trip_id": trip_id,
        "submitted_by_user_id": request.submitted_by_user_id,
        "created_at": now_fn(),
        "status": "pending",
        "target_scope": request.target_scope,
        "message": request.message,
        "flock_id": request.flock_id,
        "supporter_user_ids": request.supporter_user_ids,
        "admin_resolution": None,
    }
    db.suggestions.insert_one(suggestion)
    return {"success": True, "suggestion": suggestion}


@router.patch("/{trip_id}/suggestions/{suggestion_id}/review")
def review_suggestion_endpoint(trip_id: str, suggestion_id: str, request: SuggestionReviewRequest, db: Any = Depends(get_db)) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    actor = _require_member(trip, request.actor_user_id)
    if actor.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail={"code": "SUGGESTION_REVIEW_FORBIDDEN", "message": "Only organisers or co-leaders can review suggestions."})
    suggestion = db.suggestions.find_one({"trip_id": trip_id, "suggestion_id": suggestion_id})
    if suggestion is None:
        raise HTTPException(status_code=404, detail={"code": "SUGGESTION_NOT_FOUND", "message": "Suggestion not found."})
    suggestion["status"] = request.status
    suggestion["admin_resolution"] = {"actor_user_id": request.actor_user_id, "note": request.admin_note}
    db.suggestions.update_one({"trip_id": trip_id, "suggestion_id": suggestion_id}, {"$set": suggestion})
    return {"success": True, "suggestion": suggestion}


@router.post("/{trip_id}/itineraries/{itinerary_id}/days/{day_number}/flock-mode/start")
def start_flock_mode_endpoint(trip_id: str, itinerary_id: str, day_number: int, request: FlockModeStartRequest, db: Any = Depends(get_db)) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    _require_organiser(trip, request.actor_user_id)
    itinerary = _get_itinerary_or_404(db, itinerary_id, trip_id)
    day = _get_day_or_404(itinerary, day_number)
    day["flock_mode_active"] = True
    day["flock_mode_start_time"] = request.start_time
    day.setdefault("flocks", [])
    _persist_days(db, itinerary_id, itinerary)
    return {"success": True, "day": day}


@router.post("/{trip_id}/itineraries/{itinerary_id}/days/{day_number}/flock-mode/end")
def end_flock_mode_endpoint(trip_id: str, itinerary_id: str, day_number: int, request: FlockModeEndRequest, db: Any = Depends(get_db)) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    _require_organiser(trip, request.actor_user_id)
    itinerary = _get_itinerary_or_404(db, itinerary_id, trip_id)
    day = _get_day_or_404(itinerary, day_number)
    day["flock_mode_active"] = False
    day["flock_mode_end_time"] = request.end_time
    _persist_days(db, itinerary_id, itinerary)
    return {"success": True, "day": day}


@router.post("/{trip_id}/itineraries/{itinerary_id}/days/{day_number}/flocks")
def create_flock_endpoint(
    trip_id: str,
    itinerary_id: str,
    day_number: int,
    request: FlockCreateRequest,
    db: Any = Depends(get_db),
    id_fn: Callable[[str], str] = Depends(get_id_fn),
) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    actor = _require_member(trip, request.actor_user_id)
    if actor.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail={"code": "FLOCK_CREATE_FORBIDDEN", "message": "Only organisers or co-leaders can create Flocks."})
    _require_member(trip, request.flock_leader_user_id)
    for member_id in request.member_ids:
        _require_member(trip, member_id)
    itinerary = _get_itinerary_or_404(db, itinerary_id, trip_id)
    day = _get_day_or_404(itinerary, day_number)
    if not day.get("flock_mode_active"):
        raise HTTPException(status_code=409, detail={"code": "FLOCK_MODE_INACTIVE", "message": "Start FlockMode before creating Flocks."})
    flock_id = id_fn("flock")
    flock = {
        "flock_id": flock_id,
        "flock_name": request.flock_name,
        "flock_leader_user_id": request.flock_leader_user_id,
        "member_ids": request.member_ids,
        "schedule": request.schedule,
        "reconvene_time": request.reconvene_time,
        "reconvene_location": request.reconvene_location,
        "reconvene_coordinates": request.reconvene_coordinates,
        "chat_thread_path": _flock_chat_thread_path(trip_id, flock_id),
    }
    day.setdefault("flocks", []).append(flock)
    _persist_days(db, itinerary_id, itinerary)
    return {"success": True, "flock": flock}


@router.get("/{trip_id}/itineraries/{itinerary_id}/days/{day_number}/flocks")
def list_flocks_endpoint(trip_id: str, itinerary_id: str, day_number: int, db: Any = Depends(get_db)) -> dict[str, Any]:
    _get_trip_or_404(db, trip_id)
    itinerary = _get_itinerary_or_404(db, itinerary_id, trip_id)
    day = _get_day_or_404(itinerary, day_number)
    return {"success": True, "flocks": day.get("flocks", []), "main_chat_thread_path": f"/trips/{trip_id}/threads/main"}


@router.patch("/{trip_id}/itineraries/{itinerary_id}/days/{day_number}/flocks/{flock_id}")
def update_flock_endpoint(trip_id: str, itinerary_id: str, day_number: int, flock_id: str, request: FlockUpdateRequest, db: Any = Depends(get_db)) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    actor = _require_member(trip, request.actor_user_id)
    itinerary = _get_itinerary_or_404(db, itinerary_id, trip_id)
    day = _get_day_or_404(itinerary, day_number)
    flock = _get_flock_or_404(day, flock_id)
    if not _can_manage_flock(actor, flock):
        raise HTTPException(status_code=403, detail={"code": "FLOCK_UPDATE_FORBIDDEN", "message": "Only trip admins or this Flock leader can update this Flock."})
    updates = request.model_dump(exclude={"actor_user_id"}, exclude_none=True)
    flock.update(updates)
    flock["chat_thread_path"] = _flock_chat_thread_path(trip_id, flock_id)
    _persist_days(db, itinerary_id, itinerary)
    return {"success": True, "flock": flock}


@router.delete("/{trip_id}/itineraries/{itinerary_id}/days/{day_number}/flocks/{flock_id}")
def delete_flock_endpoint(trip_id: str, itinerary_id: str, day_number: int, flock_id: str, request: ActorRequest, db: Any = Depends(get_db)) -> dict[str, Any]:
    trip = _get_trip_or_404(db, trip_id)
    actor = _require_member(trip, request.actor_user_id)
    itinerary = _get_itinerary_or_404(db, itinerary_id, trip_id)
    day = _get_day_or_404(itinerary, day_number)
    flock = _get_flock_or_404(day, flock_id)
    if not _can_manage_flock(actor, flock):
        raise HTTPException(status_code=403, detail={"code": "FLOCK_DELETE_FORBIDDEN", "message": "Only trip admins or this Flock leader can delete this Flock."})
    day["flocks"] = [existing for existing in day.get("flocks", []) if existing.get("flock_id") != flock_id]
    _persist_days(db, itinerary_id, itinerary)
    return {"success": True, "flock_id": flock_id}


def _get_trip_or_404(db: Any, trip_id: str) -> dict[str, Any]:
    trip = db.group_trips.find_one({"trip_id": trip_id})
    if trip is None:
        raise HTTPException(status_code=404, detail={"code": "TRIP_NOT_FOUND", "message": "Trip not found."})
    return trip


def _get_itinerary_or_404(db: Any, itinerary_id: str, trip_id: str) -> dict[str, Any]:
    itinerary = db.itineraries.find_one({"itinerary_id": itinerary_id})
    if itinerary is None or itinerary.get("trip_id") != trip_id:
        raise HTTPException(status_code=404, detail={"code": "ITINERARY_NOT_FOUND", "message": "Itinerary not found."})
    return itinerary


def _get_day_or_404(itinerary: dict[str, Any], day_number: int) -> dict[str, Any]:
    for day in itinerary.get("days", []):
        if day.get("day_number") == day_number:
            return day
    raise HTTPException(status_code=404, detail={"code": "DAY_NOT_FOUND", "message": "Itinerary day not found."})


def _get_flock_or_404(day: dict[str, Any], flock_id: str) -> dict[str, Any]:
    for flock in day.get("flocks", []):
        if flock.get("flock_id") == flock_id:
            return flock
    raise HTTPException(status_code=404, detail={"code": "FLOCK_NOT_FOUND", "message": "Flock not found."})


def _find_member(trip: dict[str, Any], user_id: str) -> dict[str, Any] | None:
    for member in trip.get("members", []):
        if member.get("user_id") == user_id:
            return member
    return None


def _require_member(trip: dict[str, Any], user_id: str) -> dict[str, Any]:
    member = _find_member(trip, user_id)
    if member is None:
        raise HTTPException(status_code=404, detail={"code": "MEMBER_NOT_FOUND", "message": "Member not found."})
    return member


def _require_organiser(trip: dict[str, Any], user_id: str) -> dict[str, Any]:
    member = _require_member(trip, user_id)
    if member.get("role") != "organiser":
        raise HTTPException(status_code=403, detail={"code": "FLOCK_MODE_ORGANISER_ONLY", "message": "Only the main organiser can start or end FlockMode."})
    return member


def _member_document(user_id: str, name: str, role: str, origin_city_iata: str | None, joined_at: str) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "name": name,
        "role": role,
        "origin_city_iata": origin_city_iata,
        "joined_at": joined_at,
        "profile_complete": False,
        "shares_compliance_with_admins": True,
    }


def _co_leader_count(trip: dict[str, Any]) -> int:
    return sum(1 for member in trip.get("members", []) if member.get("role") == "co_leader")


def _can_manage_flock(actor: dict[str, Any], flock: dict[str, Any]) -> bool:
    return actor.get("role") in ADMIN_ROLES or actor.get("user_id") == flock.get("flock_leader_user_id")


def _flock_chat_thread_path(trip_id: str, flock_id: str) -> str:
    return f"/trips/{trip_id}/threads/flocks/{flock_id}"


def _persist_days(db: Any, itinerary_id: str, itinerary: dict[str, Any]) -> None:
    db.itineraries.update_one({"itinerary_id": itinerary_id}, {"$set": {"days": itinerary.get("days", [])}})


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
