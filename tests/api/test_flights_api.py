"""Tests for /flights/search and /flights/risk endpoints.

Run with: python -m pytest tests/api/test_flights_api.py -v --tb=short
"""

import pytest
from fastapi.testclient import TestClient

# Import the router directly so we avoid pulling in the full FastAPI app
# which has pre-existing import issues (get_now_fn not defined in trip.py).
from api.routes.flights_api import router as flights_api_router
from fastapi import FastAPI

# Build a minimal app with only the flights_api router.
app = FastAPI()
app.include_router(flights_api_router)
client = TestClient(app)


class TestFlightsSearch:
    def test_returns_200_with_valid_params(self):
        response = client.get("/flights/search?origin=SFO&destination=TYO&date=2026-10-15")
        assert response.status_code == 200

    def test_response_has_options_array(self):
        response = client.get("/flights/search?origin=SFO&destination=TYO&date=2026-10-15")
        assert "options" in response.json()

    def test_options_contain_flight_number_tier_and_risk_score(self):
        response = client.get("/flights/search?origin=SFO&destination=TYO&date=2026-10-15")
        data = response.json()
        options = data.get("options", [])
        assert len(options) >= 1
        first = options[0]
        assert "flight_number" in first
        assert "tier" in first
        assert "risk_score" in first or "risk" in first

    def test_tiers_are_budget_recommended_premium(self):
        response = client.get("/flights/search?origin=SFO&destination=TYO&date=2026-10-15")
        data = response.json()
        tiers = [opt["tier"] for opt in data.get("options", [])]
        assert all(t in ["budget", "recommended", "premium"] for t in tiers)

    def test_risk_score_in_expected_range(self):
        response = client.get("/flights/search?origin=SFO&destination=TYO&date=2026-10-15")
        data = response.json()
        for option in data.get("options", []):
            risk = option.get("risk_score") or option.get("risk", 50)
            assert isinstance(risk, (int, float))
            assert 0 <= risk <= 100

    def test_respects_max_budget_usd_filter(self):
        response = client.get(
            "/flights/search?origin=SFO&destination=TYO&date=2026-10-15&max_budget_usd=800"
        )
        data = response.json()
        for option in data.get("options", []):
            price = float(option.get("price_usd", 0))
            assert price <= 800, f"Flight {option.get('flight_number')} exceeds budget: {price}"

    def test_respects_preferred_airlines_filter(self):
        response = client.get(
            "/flights/search?origin=SFO&destination=TYO&date=2026-10-15&preferred_airlines=NH,UA"
        )
        data = response.json()
        for option in data.get("options", []):
            airline = option.get("airline_iata", "")
            assert airline in ["NH", "UA"], f"Unexpected airline {airline}"

    def test_400_when_origin_missing(self):
        response = client.get("/flights/search?destination=TYO&date=2026-10-15")
        assert response.status_code == 422  # FastAPI uses 422 for missing required params

    def test_400_when_destination_missing(self):
        response = client.get("/flights/search?origin=SFO&date=2026-10-15")
        assert response.status_code == 422

    def test_400_when_date_missing(self):
        response = client.get("/flights/search?origin=SFO&destination=TYO")
        assert response.status_code == 422


class TestFlightsRisk:
    def test_returns_200_with_valid_flight_params(self):
        response = client.get(
            "/flights/risk?flight_number=NH107"
            "&departure_datetime=2026-10-15T01:20:00"
            "&origin_iata=SFO&destination_iata=HND&airline_iata=NH"
        )
        assert response.status_code == 200

    def test_response_contains_risk_score_and_tier(self):
        response = client.get(
            "/flights/risk?flight_number=NH107"
            "&departure_datetime=2026-10-15T01:20:00"
            "&origin_iata=SFO&destination_iata=HND&airline_iata=NH"
        )
        data = response.json()
        assert "risk_score" in data
        assert "risk_tier" in data
        assert isinstance(data["risk_score"], (int, float))
        assert 0 <= data["risk_score"] <= 100

    def test_risk_tier_is_low_moderate_or_high(self):
        response = client.get(
            "/flights/risk?flight_number=NH107"
            "&departure_datetime=2026-10-15T01:20:00"
            "&origin_iata=SFO&destination_iata=HND&airline_iata=NH"
        )
        data = response.json()
        assert data["risk_tier"] in ["low", "moderate", "high"]

    def test_response_contains_explanation(self):
        response = client.get(
            "/flights/risk?flight_number=NH107"
            "&departure_datetime=2026-10-15T01:20:00"
            "&origin_iata=SFO&destination_iata=HND&airline_iata=NH"
        )
        data = response.json()
        assert "explanation" in data
        assert len(data["explanation"]) > 10

    def test_response_contains_dimensions(self):
        response = client.get(
            "/flights/risk?flight_number=NH107"
            "&departure_datetime=2026-10-15T01:20:00"
            "&origin_iata=SFO&destination_iata=HND&airline_iata=NH"
        )
        data = response.json()
        dimensions = data.get("dimensions", {})
        expected = [
            "on_time_performance",
            "airline_reliability",
            "time_of_day_reliability",
            "seasonal_adjustment",
            "connection_adequacy",
        ]
        for dim in expected:
            assert dim in dimensions, f"Missing dimension: {dim}"

    def test_accepts_stops_and_connection_minutes(self):
        response = client.get(
            "/flights/risk?flight_number=JL1"
            "&departure_datetime=2026-10-15T12:20:00"
            "&origin_iata=SFO&destination_iata=HND&airline_iata=JL"
            "&stops=0&connection_minutes=0&duration_minutes=655"
        )
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert data["risk_tier"] in ["low", "moderate", "high"]

    def test_400_when_flight_number_missing(self):
        response = client.get(
            "/flights/risk"
            "?departure_datetime=2026-10-15T01:20:00"
            "&origin_iata=SFO&destination_iata=HND&airline_iata=NH"
        )
        assert response.status_code == 422  # FastAPI uses 422 for missing required params