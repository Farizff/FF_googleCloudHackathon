import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parents[2] / "db" / "seed" / "seed_venues_tokyo.json"

REQUIRED_FIELDS = {
    "venue_id",
    "name",
    "category",
    "coordinates",
    "cluster",
    "opening_hours",
    "dietary_tags",
    "mobility",
    "physical_intensity",
    "estimated_duration_minutes",
    "price_level",
    "booking_required",
}

DEMO_VENUE_NAMES = {
    "teamLab Borderless",
    "Tsukiji Outer Market",
    "Yanaka Ginza",
    "Takeshita Street",
    "Shibuya Crossing",
    "Shinjuku Station East Exit",
    "Mori Art Museum",
}


def load_venues() -> list[dict]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def test_tokyo_venue_seed_has_at_least_25_deterministic_records_with_required_fields():
    venues = load_venues()

    assert isinstance(venues, list)
    assert len(venues) >= 25

    venue_ids = [venue["venue_id"] for venue in venues]
    assert venue_ids == sorted(venue_ids)
    assert len(venue_ids) == len(set(venue_ids))

    for venue in venues:
        assert set(venue) == REQUIRED_FIELDS
        assert venue["venue_id"].startswith("tokyo_")
        assert venue["name"]
        assert venue["category"]
        assert venue["cluster"]
        assert set(venue["coordinates"]) == {"lat", "lng"}
        assert 35.5 <= venue["coordinates"]["lat"] <= 35.9
        assert 139.5 <= venue["coordinates"]["lng"] <= 140.1
        assert set(venue["opening_hours"]) == {"open", "close"}
        assert venue["opening_hours"]["open"] < venue["opening_hours"]["close"]
        assert isinstance(venue["dietary_tags"], list)
        assert isinstance(venue["mobility"], dict)
        assert set(venue["mobility"]) == {"wheelchair_accessible", "stairs_required", "rest_seating"}
        assert venue["physical_intensity"] in {"low", "medium", "high"}
        assert 30 <= venue["estimated_duration_minutes"] <= 240
        assert venue["price_level"] in {"free", "low", "medium", "high"}
        assert isinstance(venue["booking_required"], bool)


def test_tokyo_venue_seed_covers_judge_demo_flockmode_and_disruption_venues():
    venues = load_venues()
    venues_by_name = {venue["name"]: venue for venue in venues}

    assert DEMO_VENUE_NAMES <= set(venues_by_name)
    assert venues_by_name["teamLab Borderless"]["cluster"] == "odaiba_azabudai"
    assert venues_by_name["Tsukiji Outer Market"]["dietary_tags"] == ["seafood", "street_food"]
    assert venues_by_name["Takeshita Street"]["cluster"] == "harajuku_shibuya"
    assert venues_by_name["Shinjuku Station East Exit"]["category"] == "meeting_point"
    assert venues_by_name["Mori Art Museum"]["booking_required"] is True


def test_tokyo_venue_seed_has_balanced_clusters_categories_and_accessibility_metadata():
    venues = load_venues()

    clusters = {venue["cluster"] for venue in venues}
    categories = {venue["category"] for venue in venues}

    assert {
        "asakusa_ueno",
        "harajuku_shibuya",
        "shinjuku",
        "ginza_tsukiji",
        "odaiba_azabudai",
    } <= clusters
    assert {
        "temple",
        "market",
        "museum",
        "shopping_street",
        "park",
        "observation_deck",
        "meeting_point",
        "restaurant",
    } <= categories
    assert any(venue["mobility"]["wheelchair_accessible"] is True for venue in venues)
    assert any(venue["mobility"]["stairs_required"] is True for venue in venues)
    assert any(venue["booking_required"] is True for venue in venues)
    assert any("vegetarian" in venue["dietary_tags"] for venue in venues)
