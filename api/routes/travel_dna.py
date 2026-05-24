from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db.client import get_database

router = APIRouter(prefix="/travel-dna", tags=["traveller"])


def get_db() -> Any:
    return get_database()


class TravelDNAResponse(BaseModel):
    user_id: str
    travel_dna: dict[str, Any]


def compute_travel_dna(profile: dict[str, Any]) -> str:
    """Rule-based computation of primary_style from traveller profile fields."""
    prefs = profile.get("preferences", {})
    pace = prefs.get("pace", "moderate")
    interests = set(prefs.get("interests", []))
    crowd_tolerance = prefs.get("crowd_tolerance", "neutral")
    physical_fitness = profile.get("physical_fitness", "average")

    # Adrenaline junkie: packed pace + (nightlife OR sport)
    if pace == "packed" and (interests & {"nightlife", "sport"}):
        return "adrenaline_junkie"

    # Zen explorer: relaxed pace + (nature OR wellness)
    if pace == "relaxed" and (interests & {"nature", "wellness"}):
        return "zen_explorer"

    # Cultural connoisseur: moderate pace + (art OR culture OR history)
    if pace == "moderate" and (interests & {"art", "culture", "history"}):
        return "cultural_connoisseur"

    # Foodie adventurer: food interest + crowd-tolerant
    if "food" in interests and crowd_tolerance == "tolerate":
        return "foodie_adventurer"

    # Default
    return "balanced_explorer"


@router.get("/{user_id}", response_model=TravelDNAResponse)
def get_travel_dna(user_id: str, db: Any = Depends(get_db)) -> dict[str, Any]:
    """Compute and store travel DNA for a traveller, then return it."""
    profile = db.traveller_profiles.find_one({"user_id": user_id})
    if profile is None:
        raise HTTPException(status_code=404, detail={"code": "PROFILE_NOT_FOUND", "message": f"Traveller '{user_id}' not found."})

    primary_style = compute_travel_dna(profile)
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    travel_dna = {
        "primary_style": primary_style,
        "energy_level": profile.get("physical_fitness", "average"),
        "last_updated": now,
    }

    db.traveller_profiles.update_one(
        {"user_id": user_id},
        {"$set": {"travel_dna": travel_dna}},
    )

    return {"user_id": user_id, "travel_dna": travel_dna}