from datetime import UTC, datetime
from typing import Any, Callable
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _default_itinerary_id() -> str:
    return f"iti_{uuid4().hex}"


def save_itinerary(
    itinerary: dict[str, Any],
    collection: Any,
    firebase_broadcaster: Any | None = None,
    clock: Callable[[], str] = _utc_now_iso,
    id_factory: Callable[[], str] = _default_itinerary_id,
) -> dict[str, Any]:
    """Upsert an itinerary into an injected collection and optionally broadcast it."""
    itinerary_id = itinerary.get("itinerary_id") or id_factory()
    updated_at = clock()
    saved_itinerary = {
        **itinerary,
        "itinerary_id": itinerary_id,
        "updated_at": updated_at,
    }

    collection.update_one(
        {"itinerary_id": itinerary_id},
        {"$set": saved_itinerary},
        upsert=True,
    )

    if firebase_broadcaster is not None:
        firebase_broadcaster.broadcast_itinerary_saved(saved_itinerary)

    return {
        "success": True,
        "itinerary_id": itinerary_id,
        "updated_at": updated_at,
    }
