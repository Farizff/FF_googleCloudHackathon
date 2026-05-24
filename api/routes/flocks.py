from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from db.client import get_database

router = APIRouter(prefix="/flocks", tags=["flocks"])


def get_db() -> Any:
    return get_database()


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class CreateFlockRequest(BaseModel):
    flock_name: str
    leader_user_id: str
    member_ids: list[str]
    trip_id: str
    reconvene_time: str
    reconvene_location: str
    reconvene_coordinates: dict[str, float] | None = None
    day_number: int | None = None
    activity: str | None = None


class FlockResponse(BaseModel):
    flock_id: str
    flock_name: str
    leader_user_id: str
    member_ids: list[str]
    trip_id: str
    reconvene_time: str | None = None
    reconvene_location: str | None = None
    reconvene_coordinates: dict[str, float] | None = None
    day_number: int | None = None
    activity: str | None = None


@router.post("", response_model=FlockResponse)
def create_flock(request: CreateFlockRequest, db: Any = Depends(get_db)) -> dict[str, Any]:
    """Create a new flock within a trip."""
    trip = db.group_trips.find_one({"trip_id": request.trip_id})
    if trip is None:
        raise HTTPException(status_code=404, detail={"code": "TRIP_NOT_FOUND", "message": f"Trip '{request.trip_id}' not found."})

    flock_id = f"flock_{uuid4().hex[:12]}"
    now = _utc_now_iso()

    flock = {
        "flock_id": flock_id,
        "flock_name": request.flock_name,
        "leader_user_id": request.leader_user_id,
        "member_ids": request.member_ids,
        "trip_id": request.trip_id,
        "reconvene_time": request.reconvene_time,
        "reconvene_location": request.reconvene_location,
        "reconvene_coordinates": request.reconvene_coordinates,
        "day_number": request.day_number,
        "activity": request.activity,
        "created_at": now,
    }

    db.flocks.insert_one(flock)
    return flock


@router.get("", response_model=list[FlockResponse])
def list_flocks(trip_id: str = Query(...), db: Any = Depends(get_db)) -> list[dict[str, Any]]:
    """List all flocks for a given trip."""
    return list(db.flocks.find({"trip_id": trip_id}))


@router.get("/{flock_id}", response_model=FlockResponse)
def get_flock(flock_id: str, db: Any = Depends(get_db)) -> dict[str, Any]:
    """Get a single flock with its member list."""
    flock = db.flocks.find_one({"flock_id": flock_id})
    if flock is None:
        raise HTTPException(status_code=404, detail={"code": "FLOCK_NOT_FOUND", "message": f"Flock '{flock_id}' not found."})
    return flock