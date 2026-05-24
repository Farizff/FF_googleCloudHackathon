from typing import Any

from agent.tools.poll_flight_status import poll_flight_status

ACTIVE_ITINERARY_STATUSES = {"confirmed", "active"}


def poll_active_trip_flights(
    db: Any,
    now_iso: str,
    aerodatabox_client: Any,
    pubsub_publisher: Any,
) -> dict[str, int]:
    """Poll flights attached to confirmed/active itineraries and persist changes."""
    itineraries = [itinerary for itinerary in db.itineraries.find({}) if itinerary.get("status") in ACTIVE_ITINERARY_STATUSES]
    result = {"itineraries_scanned": len(itineraries), "flights_polled": 0, "status_changes": 0}

    for itinerary in itineraries:
        changed = False
        for flight in itinerary.get("flights", []):
            flight_number = flight.get("flight_number")
            departure_date = flight.get("departure_date") or _date_from_datetime(flight.get("departure_datetime"))
            if not flight_number or not departure_date:
                continue

            previous_status = flight.get("live_status") or flight.get("status")
            status = poll_flight_status(
                flight_number=flight_number,
                departure_date=departure_date,
                cache_collection=db.flight_status_cache,
                aerodatabox_client=aerodatabox_client,
                pubsub_publisher=pubsub_publisher,
                clock=lambda: now_iso,
            )
            result["flights_polled"] += 1
            current_status = status.get("status") or "unknown"
            if previous_status != current_status:
                result["status_changes"] += 1
            flight["live_status"] = current_status
            flight["live_status_last_polled"] = now_iso
            if status.get("delay_minutes") is not None:
                flight["delay_minutes"] = status["delay_minutes"]
            changed = True

        if changed:
            db.itineraries.update_one(
                {"itinerary_id": itinerary.get("itinerary_id")},
                {"$set": {"flights": itinerary.get("flights", [])}},
            )

    return result


def _date_from_datetime(value: Any) -> str | None:
    if isinstance(value, str) and len(value) >= 10:
        return value[:10]
    return None
