import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parents[2] / "db" / "seed" / "visa_requirements.json"
DEMO_TRIP_PATH = Path(__file__).resolve().parents[2] / "db" / "seed" / "seed_demo_trip.json"

REQUIRED_FIELDS = {
    "passport_iso",
    "destination_iso",
    "visa_required",
    "visa_type",
    "processing_days_min",
    "processing_days_max",
    "official_url",
    "fee_usd_estimate",
    "notes",
    "last_verified",
}

REQUIRED_PRD_PAIRS = {
    ("IDN", "JPN"), ("IDN", "SGP"), ("IDN", "AUS"), ("IDN", "USA"), ("IDN", "GBR"), ("IDN", "SCH"),
    ("IND", "JPN"), ("IND", "USA"), ("IND", "GBR"), ("IND", "SCH"), ("IND", "SGP"), ("IND", "AUS"),
    ("USA", "JPN"), ("USA", "CHN"), ("USA", "BRA"), ("USA", "SCH"), ("USA", "GBR"), ("USA", "AUS"),
    ("GBR", "USA"), ("GBR", "JPN"), ("GBR", "AUS"), ("GBR", "SCH"),
    ("PHL", "JPN"), ("PHL", "SGP"), ("PHL", "USA"), ("PHL", "SCH"),
    ("BRA", "JPN"), ("BRA", "USA"), ("BRA", "SCH"), ("BRA", "GBR"),
    ("EGY", "JPN"), ("EGY", "USA"), ("EGY", "GBR"),
    ("MEX", "JPN"), ("MEX", "USA"), ("MEX", "GBR"), ("MEX", "SCH"),
}


def load_requirements() -> list[dict]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def test_visa_requirements_seed_covers_prd_common_pairs():
    records = load_requirements()
    pairs = {(record["passport_iso"], record["destination_iso"]) for record in records}

    assert REQUIRED_PRD_PAIRS <= pairs
    assert len(records) >= 30


def test_visa_requirements_records_have_required_validation_fields():
    records = load_requirements()
    pairs = [(record["passport_iso"], record["destination_iso"]) for record in records]

    assert pairs == sorted(pairs)
    assert len(pairs) == len(set(pairs))

    for record in records:
        assert set(record) == REQUIRED_FIELDS
        assert len(record["passport_iso"]) == 3
        assert len(record["destination_iso"]) == 3
        assert isinstance(record["visa_required"], bool)
        assert record["visa_type"]
        assert 0 <= record["processing_days_min"] <= record["processing_days_max"]
        assert record["fee_usd_estimate"] >= 0
        assert record["official_url"].startswith("https://")
        assert record["notes"]
        assert record["last_verified"] == "2026-05-23"


def test_visa_requirements_support_private_demo_compliance_reminders():
    records_by_pair = {
        (record["passport_iso"], record["destination_iso"]): record
        for record in load_requirements()
    }
    demo_trip = json.loads(DEMO_TRIP_PATH.read_text(encoding="utf-8"))
    private_reminders = demo_trip["private_compliance_reminders"]

    reminder_pairs = {(reminder["passport_iso"], reminder["destination_iso"]) for reminder in private_reminders}
    assert reminder_pairs == {("IND", "JPN"), ("EGY", "JPN")}
    assert records_by_pair[("IND", "JPN")]["visa_required"] is True
    assert records_by_pair[("EGY", "JPN")]["visa_required"] is True
    assert records_by_pair[("USA", "JPN")]["visa_required"] is False
    assert records_by_pair[("MEX", "JPN")]["visa_required"] is False
    assert records_by_pair[("BRA", "JPN")]["visa_required"] is False
