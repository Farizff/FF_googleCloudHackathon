import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from db.client import get_database


router = APIRouter(prefix="/judge")
SEED_PATH = Path(__file__).resolve().parents[2] / "db" / "seed" / "seed_demo_trip.json"
DEMO_ITINERARY_ID = "iti_tokyo_reunion_2026"
DEMO_DISRUPTION_DESCRIPTION = "Day 3 flight UA837 cancelled — judge demo disruption."


def get_db() -> Any:
    return get_database()


def get_now_fn() -> Callable[[], str]:
    return _utc_now_iso


@router.post("/seed-demo-trip")
def seed_demo_trip_endpoint(db: Any = Depends(get_db)) -> dict[str, Any]:
    return seed_demo_trip(db)


@router.post("/reset")
def reset_judge_demo_endpoint(db: Any = Depends(get_db)) -> dict[str, Any]:
    seed = _load_seed()
    trip = seed["group_trip"]
    trip_id = trip["trip_id"]
    member_ids = [member["user_id"] for member in trip["members"]]

    db.group_trips.delete_many({"trip_id": trip_id})
    db.traveller_profiles.delete_many({"user_id": {"$in": member_ids}})
    db.compliance_reminders.delete_many({"trip_id": trip_id})
    db.flocks.delete_many({"trip_id": trip_id})
    db.disruption_events.delete_many({"itinerary_id": DEMO_ITINERARY_ID})

    return {"success": True, "reset": True, "seeded": seed_demo_trip(db, seed)}


@router.post("/trigger-disruption")
def judge_trigger_disruption_endpoint(
    db: Any = Depends(get_db),
    now_fn: Callable[[], str] = Depends(get_now_fn),
) -> dict[str, Any]:
    event = {
        "itinerary_id": DEMO_ITINERARY_ID,
        "event_type": "flight_cancellation",
        "description": DEMO_DISRUPTION_DESCRIPTION,
        "affected_day_numbers": [3],
        "created_at": now_fn(),
        "judge_demo": True,
    }
    db.disruption_events.insert_one(event)
    return {
        "success": True,
        "event_type": event["event_type"],
        "itinerary_id": event["itinerary_id"],
        "affected_day_numbers": event["affected_day_numbers"],
        "description": event["description"],
    }


@router.get("/instructions", response_class=PlainTextResponse)
def judge_instructions_endpoint() -> str:
    return """Bounce Judge Test Mode

Use these endpoints to test Bounce without setup:

POST /judge/reset
- Clears the demo state and reseeds The Tokyo Reunion.

POST /judge/seed-demo-trip
- Creates The Tokyo Reunion with 10 pre-loaded members, private compliance reminders, and FlockMode groups.

POST /judge/trigger-disruption
- Fires the Day 3 UA837 cancellation demo disruption.

Suggested path:
1. Reset the demo.
2. Open The Tokyo Reunion.
3. Trigger disruption and confirm alternatives/update flow.
4. Test FlockMode, split bill, visa, and flight status screens.
"""


def seed_demo_trip(db: Any, seed: dict[str, Any] | None = None) -> dict[str, Any]:
    seed_data = seed or _load_seed()
    trip = deepcopy(seed_data["group_trip"])
    trip_id = trip["trip_id"]

    db.group_trips.replace_one({"trip_id": trip_id}, trip, upsert=True)

    profiles = deepcopy(seed_data.get("traveller_profiles", []))
    for profile in profiles:
        db.traveller_profiles.replace_one({"user_id": profile["user_id"]}, profile, upsert=True)

    reminders = deepcopy(seed_data.get("private_compliance_reminders", []))
    for reminder in reminders:
        document = {"trip_id": trip_id, **reminder}
        db.compliance_reminders.replace_one(
            {"trip_id": trip_id, "user_id": reminder["user_id"], "destination_iso": reminder["destination_iso"]},
            document,
            upsert=True,
        )

    flocks = _flock_documents(seed_data, trip_id)
    for flock in flocks:
        db.flocks.replace_one({"trip_id": trip_id, "flock_id": flock["flock_id"]}, flock, upsert=True)

    return {
        "success": True,
        "trip_id": trip_id,
        "trip_name": trip["trip_name"],
        "members_seeded": len(trip.get("members", [])),
        "profiles_seeded": len(profiles),
        "compliance_reminders_seeded": len(reminders),
        "flocks_seeded": len(flocks),
    }


def _flock_documents(seed_data: dict[str, Any], trip_id: str) -> list[dict[str, Any]]:
    flock_mode = seed_data.get("flock_mode") or {}
    common = {
        "trip_id": trip_id,
        "day_number": flock_mode.get("day_number"),
        "reconvene_time": flock_mode.get("reconvene_time"),
        "reconvene_location": flock_mode.get("reconvene_location"),
        "reconvene_coordinates": flock_mode.get("reconvene_coordinates"),
    }
    return [{**common, **deepcopy(flock)} for flock in flock_mode.get("flocks", [])]


def _load_seed() -> dict[str, Any]:
    with SEED_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
