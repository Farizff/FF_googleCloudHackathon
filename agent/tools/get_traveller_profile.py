from typing import Any


USER_NOT_FOUND = "USER_NOT_FOUND"


def get_traveller_profile(user_id: str, collection: Any) -> dict[str, Any]:
    """Return a traveller profile from an injected Mongo-like collection."""
    profile = collection.find_one({"user_id": user_id})

    if profile is None:
        return {
            "error": {
                "code": USER_NOT_FOUND,
                "message": f"Traveller profile not found for user_id '{user_id}'.",
            }
        }

    return {"profile": profile}
