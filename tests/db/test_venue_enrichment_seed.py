import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parents[2] / "db" / "seed" / "venue_enrichment.json"
VENUE_SEED_PATH = Path(__file__).resolve().parents[2] / "db" / "seed" / "seed_venues_tokyo.json"

REQUIRED_FIELDS = {
    "category_pattern",
    "google_place_types",
    "physical_intensity",
    "estimated_duration_minutes",
    "crowd_peak_weekday",
    "crowd_peak_weekend",
    "customs",
    "dietary_relevance",
    "child_friendly",
    "elderly_friendly",
    "wheelchair_accessibility",
}

REQUIRED_CATEGORY_DEFAULTS = {
    "temple",
    "museum",
    "market",
    "shopping_street",
    "park",
    "observation_deck",
    "meeting_point",
    "restaurant",
}


def load_enrichment() -> list[dict]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def test_venue_enrichment_seed_covers_required_category_defaults_for_search_venues():
    records = load_enrichment()
    patterns = {record["category_pattern"] for record in records}

    assert REQUIRED_CATEGORY_DEFAULTS <= patterns
    assert len(records) >= len(REQUIRED_CATEGORY_DEFAULTS)


def test_venue_enrichment_records_have_search_venues_fields_and_safe_defaults():
    records = load_enrichment()
    patterns = [record["category_pattern"] for record in records]

    assert patterns == sorted(patterns)
    assert len(patterns) == len(set(patterns))

    for record in records:
        assert set(record) == REQUIRED_FIELDS
        assert record["category_pattern"]
        assert record["google_place_types"]
        assert all(isinstance(place_type, str) and place_type for place_type in record["google_place_types"])
        assert record["physical_intensity"] in {"low", "medium", "high"}
        assert 30 <= record["estimated_duration_minutes"] <= 240
        assert_valid_peak_window(record["crowd_peak_weekday"])
        assert_valid_peak_window(record["crowd_peak_weekend"])
        assert isinstance(record["customs"], dict)
        assert "behavioural_notes" in record["customs"]
        assert isinstance(record["dietary_relevance"], str)
        assert isinstance(record["child_friendly"], bool)
        assert isinstance(record["elderly_friendly"], bool)
        assert record["wheelchair_accessibility"] in {"full", "partial", "varies", "limited"}


def test_venue_enrichment_supports_existing_tokyo_demo_venue_categories():
    records_by_pattern = {record["category_pattern"]: record for record in load_enrichment()}
    tokyo_venues = json.loads(VENUE_SEED_PATH.read_text(encoding="utf-8"))
    demo_categories = {venue["category"] for venue in tokyo_venues}

    assert REQUIRED_CATEGORY_DEFAULTS <= demo_categories
    for category in REQUIRED_CATEGORY_DEFAULTS:
        enrichment = records_by_pattern[category]
        assert enrichment["google_place_types"]
        assert enrichment["estimated_duration_minutes"] > 0

    assert records_by_pattern["temple"]["customs"]["shoes_off"] is True
    assert records_by_pattern["restaurant"]["dietary_relevance"] == "high"
    assert records_by_pattern["meeting_point"]["estimated_duration_minutes"] <= 45


def assert_valid_peak_window(window: dict):
    assert set(window) == {"start", "end"}
    assert window["start"] < window["end"]
    assert len(window["start"]) == 5
    assert len(window["end"]) == 5
    assert window["start"][2] == ":"
    assert window["end"][2] == ":"
