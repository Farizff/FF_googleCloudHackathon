import json
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "db" / "schemas"

EXPECTED_COLLECTIONS = {
    "traveller_profiles": {"user_id", "name", "passport_country", "dietary", "preferences"},
    "group_trips": {"trip_id", "invite_token", "members", "destination_iata", "status"},
    "itineraries": {"itinerary_id", "trip_id", "days", "flights", "status"},
    "flight_performance": {"route_key", "airline_iata", "on_time_pct", "departure_time_reliability", "seasonal_risk"},
    "airline_ratings": {"iata", "name", "skytrax_rating", "airhelp_score", "last_verified"},
    "visa_requirements": {"passport_iso", "destination_iso", "visa_required", "official_url", "last_verified"},
    "venue_enrichment": {"category_pattern", "google_place_types", "physical_intensity", "customs"},
    "expenses": {"expense_id", "trip_id", "logged_by_user_id", "amount_usd", "participants"},
    "suggestions": {"suggestion_id", "trip_id", "submitted_by_user_id", "status", "target_scope"},
    "notification_log": {"notification_id", "trip_id", "recipient", "channel", "status"},
}


def load_schema(collection: str) -> dict:
    path = SCHEMA_DIR / f"{collection}.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_prd_mongodb_collection_schemas_exist_and_exclude_firebase_chat_threads():
    """PRD v2.1 requires exactly 10 MongoDB collection schema artifacts; chat stays in Firebase."""
    actual = {path.name for path in SCHEMA_DIR.glob("*.schema.json")}
    expected = {f"{collection}.schema.json" for collection in EXPECTED_COLLECTIONS}

    assert actual == expected
    assert "chat_threads.schema.json" not in actual


def test_each_schema_names_its_collection_and_required_prd_fields():
    """Schema files must encode the PRD collection intent, not just exist as empty placeholders."""
    for collection, required_fields in EXPECTED_COLLECTIONS.items():
        schema = load_schema(collection)

        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["title"] == collection
        assert schema["type"] == "object"
        assert required_fields.issubset(set(schema["required"]))
        assert required_fields.issubset(set(schema["properties"]))
