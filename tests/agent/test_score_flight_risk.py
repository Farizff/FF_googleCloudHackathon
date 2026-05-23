from agent.tools.score_flight_risk import score_flight_risk


class FakeCollection:
    def __init__(self, records):
        self.records = records
        self.queries = []

    def find_one(self, query):
        self.queries.append(query)
        for record in self.records:
            if all(record.get(key) == value for key, value in query.items()):
                return record
        return None


def ua79_performance():
    return {
        "route_id": "jfk_nrt_budget_ua79",
        "route_key": "JFK-NRT",
        "airline_iata": "UA",
        "flight_number": "UA79",
        "on_time_pct": 0.68,
        "departure_time_reliability": {
            "early_morning": 88,
            "morning": 82,
            "afternoon": 70,
            "evening": 65,
        },
        "seasonal_risk": {"07": {"risk_multiplier": 1.12}},
    }


def test_score_flight_risk_uses_seeded_route_weighted_formula():
    """Known route records should use every PRD dimension with exact weights."""
    flight_performance = FakeCollection([ua79_performance()])
    airline_ratings = FakeCollection([{"iata": "UA", "skytrax_rating": 3}])

    result = score_flight_risk(
        {
            "route_id": "jfk_nrt_budget_ua79",
            "route_key": "JFK-NRT",
            "airline_iata": "UA",
            "flight_number": "UA79",
            "scheduled_departure_local": "2026-07-03T11:15:00-04:00",
            "stops": 1,
            "connection_minutes": 105,
        },
        flight_performance_collection=flight_performance,
        airline_ratings_collection=airline_ratings,
    )

    assert result["risk_score"] == 72
    assert result["risk_tier"] == "moderate"
    assert result["dimensions"] == {
        "on_time_performance": 68.0,
        "airline_reliability": 60.0,
        "time_of_day_reliability": 82.0,
        "seasonal_adjustment": 89.29,
        "connection_adequacy": 80.0,
    }
    assert "72/100" in result["explanation"]
    assert flight_performance.queries[0] == {"route_id": "jfk_nrt_budget_ua79"}
    assert airline_ratings.queries == [{"iata": "UA"}]


def test_score_flight_risk_uses_fallbacks_and_amadeus_prediction_when_route_missing():
    """Missing route performance should still produce a deterministic score."""
    result = score_flight_risk(
        {
            "route_key": "SFO-NRT",
            "airline_iata": "ZZ",
            "flight_number": "ZZ100",
            "scheduled_departure_local": "2026-03-04T06:30:00-08:00",
            "stops": 0,
            "connection_minutes": 0,
        },
        flight_performance_collection=FakeCollection([]),
        airline_ratings_collection=FakeCollection([]),
        amadeus_delay_prediction=0.42,
    )

    assert result["dimensions"] == {
        "on_time_performance": 42.0,
        "airline_reliability": 60.0,
        "time_of_day_reliability": 88.0,
        "seasonal_adjustment": 100.0,
        "connection_adequacy": 100.0,
    }
    assert result["risk_score"] == 67
    assert result["risk_tier"] == "moderate"


def test_score_flight_risk_connection_boundaries_drive_risk_tiers():
    """Connection adequacy boundaries should match the PRD exactly."""
    common = {
        "route_key": "A-B",
        "airline_iata": "AA",
        "scheduled_departure_local": "2026-03-04T21:30:00-08:00",
    }
    airline_ratings = FakeCollection([{"iata": "AA", "skytrax_rating": 5}])
    flight_performance = FakeCollection([])

    direct = score_flight_risk(
        {**common, "stops": 0, "connection_minutes": 0},
        flight_performance,
        airline_ratings,
        amadeus_delay_prediction=1.0,
    )
    long_connection = score_flight_risk(
        {**common, "stops": 1, "connection_minutes": 91},
        flight_performance,
        airline_ratings,
        amadeus_delay_prediction=1.0,
    )
    medium_connection = score_flight_risk(
        {**common, "stops": 1, "connection_minutes": 60},
        flight_performance,
        airline_ratings,
        amadeus_delay_prediction=0.35,
    )
    short_connection = score_flight_risk(
        {**common, "airline_iata": "ZZ", "stops": 1, "connection_minutes": 59},
        flight_performance,
        airline_ratings,
        amadeus_delay_prediction=0.0,
    )

    assert direct["dimensions"]["connection_adequacy"] == 100.0
    assert direct["risk_tier"] == "low"
    assert long_connection["dimensions"]["connection_adequacy"] == 80.0
    assert long_connection["risk_tier"] == "low"
    assert medium_connection["dimensions"]["connection_adequacy"] == 60.0
    assert medium_connection["risk_tier"] == "moderate"
    assert short_connection["dimensions"]["connection_adequacy"] == 30.0
    assert short_connection["risk_tier"] == "high"


def test_score_flight_risk_can_lookup_route_by_composite_when_route_id_missing():
    """Flight options without route_id should still match seeded route details."""
    flight_performance = FakeCollection([ua79_performance()])

    result = score_flight_risk(
        {
            "route_key": "JFK-NRT",
            "airline_iata": "UA",
            "flight_number": "UA79",
            "scheduled_departure_local": "2026-07-03T11:15:00-04:00",
            "stops": 1,
            "connection_minutes": 105,
        },
        flight_performance_collection=flight_performance,
        airline_ratings_collection=FakeCollection([{"iata": "UA", "skytrax_rating": 3}]),
    )

    assert result["risk_score"] == 72
    assert flight_performance.queries == [
        {"route_key": "JFK-NRT", "airline_iata": "UA", "flight_number": "UA79"}
    ]


def test_score_flight_risk_returns_standard_error_for_invalid_departure_datetime():
    """Invalid timestamps should fail loud instead of silently mis-scoring flights."""
    result = score_flight_risk(
        {
            "route_key": "A-B",
            "airline_iata": "AA",
            "scheduled_departure_local": "not-a-date",
            "stops": 0,
            "connection_minutes": 0,
        },
        flight_performance_collection=FakeCollection([]),
        airline_ratings_collection=FakeCollection([]),
    )

    assert result == {
        "error": {
            "code": "INVALID_DEPARTURE_DATETIME",
            "message": "Invalid scheduled_departure_local 'not-a-date'.",
        }
    }
