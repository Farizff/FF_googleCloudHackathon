import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parents[2] / "db" / "seed" / "seed_flight_performance.json"
DEMO_TRIP_PATH = Path(__file__).resolve().parents[2] / "db" / "seed" / "seed_demo_trip.json"

EXPECTED_ORIGINS = {"SFO", "LAX", "JFK", "SEA", "ORD"}
EXPECTED_TIERS = {"budget", "recommended", "premium"}
RELIABILITY_SLOTS = {"early_morning", "morning", "afternoon", "evening"}
REQUIRED_FIELDS = {
    "route_id",
    "route_key",
    "origin_iata",
    "destination_iata",
    "airline_iata",
    "airline_name",
    "flight_number",
    "option_tier",
    "stops",
    "connection_minutes",
    "scheduled_departure_local",
    "scheduled_arrival_local",
    "duration_minutes",
    "estimated_price_usd",
    "risk_score",
    "risk_tier",
    "on_time_pct",
    "average_delay_minutes",
    "cancellation_pct",
    "sample_size",
    "departure_time_reliability",
    "seasonal_risk",
    "judge_fallback",
    "last_verified",
}


def load_seed() -> list[dict]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def test_flight_performance_seed_has_deterministic_records_for_demo_origins():
    """The judge demo needs three flight options for each Reunion origin city."""
    records = load_seed()
    demo_trip = json.loads(DEMO_TRIP_PATH.read_text(encoding="utf-8"))
    member_origins = {member["origin_city_iata"] for member in demo_trip["group_trip"]["members"]}

    assert member_origins == EXPECTED_ORIGINS
    assert isinstance(records, list)
    assert len(records) == 15

    route_ids = [record["route_id"] for record in records]
    assert route_ids == sorted(route_ids)
    assert len(route_ids) == len(set(route_ids))

    origins = {record["origin_iata"] for record in records}
    assert origins == member_origins
    for origin in EXPECTED_ORIGINS:
        origin_records = [record for record in records if record["origin_iata"] == origin]
        assert {record["option_tier"] for record in origin_records} == EXPECTED_TIERS
        assert {record["destination_iata"] for record in origin_records} == {"NRT"}


def test_flight_performance_seed_contains_prd_demo_flights_and_judge_fallbacks():
    """PRD/demo script names NH106, UA837, and the SFO risk card explicitly."""
    records = load_seed()
    records_by_flight = {record["flight_number"]: record for record in records}

    assert "NH106" in records_by_flight
    assert "UA837" in records_by_flight
    assert "UA838" in records_by_flight

    nh106 = records_by_flight["NH106"]
    assert nh106["route_id"] == "sfo_nrt_recommended_nh106"
    assert nh106["route_key"] == "SFO-NRT"
    assert nh106["airline_iata"] == "NH"
    assert nh106["option_tier"] == "recommended"
    assert nh106["risk_score"] == 84
    assert nh106["risk_tier"] == "low"
    assert nh106["stops"] == 0

    ua837 = records_by_flight["UA837"]
    assert ua837["route_id"] == "sfo_nrt_fallback_ua837"
    assert ua837["judge_fallback"]["demo_event"] == "day_3_flight_cancelled"
    assert ua837["judge_fallback"]["fallback_reason"] == "AeroDataBox unavailable or Amadeus approval delayed"
    assert ua837["judge_fallback"]["status_override"] == "cancelled"


def test_flight_performance_records_have_reliability_and_seasonal_fields_for_risk_scoring():
    records = load_seed()

    for record in records:
        assert set(record) == REQUIRED_FIELDS
        assert record["route_key"] == f"{record['origin_iata']}-{record['destination_iata']}"
        assert record["destination_iata"] == "NRT"
        assert record["risk_tier"] in {"low", "moderate", "high"}
        assert 0 <= record["risk_score"] <= 100
        assert 0 <= record["on_time_pct"] <= 1
        assert record["average_delay_minutes"] >= 0
        assert 0 <= record["cancellation_pct"] <= 1
        assert record["sample_size"] >= 100
        assert isinstance(record["judge_fallback"]["enabled"], bool)

        assert set(record["departure_time_reliability"]) == RELIABILITY_SLOTS
        for slot_score in record["departure_time_reliability"].values():
            assert 0 <= slot_score <= 100

        assert "07" in record["seasonal_risk"]
        for month, risk in record["seasonal_risk"].items():
            assert month in {"01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"}
            assert set(risk) == {"risk_multiplier", "notes"}
            assert risk["risk_multiplier"] > 0
            assert risk["notes"]
