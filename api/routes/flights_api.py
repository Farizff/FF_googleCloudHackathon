"""Flight search and risk-scoring API endpoints.

GET /flights/search?origin=X&destination=Y&date=YYYY-MM-DD
GET /flights/risk?flight_number=X&departure_datetime=Y&origin_iata=Z&destination_iata=W&airline_iata=K&stops=N
"""

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from agent.tools.search_flights import search_flights
from agent.tools.score_flight_risk import score_flight_risk

router = APIRouter(prefix="/flights", tags=["flights"])


# ---------------------------------------------------------------------------
# FakeAmadeusClient — used when no live Amadeus credentials are available.
# ---------------------------------------------------------------------------


class FakeAmadeusClient:
    """Returns deterministic flight offers for demo / test use."""

    def __init__(self, offers: list[dict[str, Any]] | None = None):
        self._offers = offers or _default_offers()
        self.calls: list[dict[str, Any]] = []

    def flight_offers_search(self, **kwargs: Any) -> list[dict[str, Any]]:
        self.calls.append(kwargs)
        return list(self._offers)


class FakeRiskScorer:
    """Returns deterministic risk scores for demo / test use."""

    def __init__(self):
        self.calls: list[dict[str, Any]] = []

    def score(self, flight: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(flight)
        flight_number = flight.get("flight_number", "")
        stops = int(flight.get("stops") or 0)
        if "NH" in flight_number:
            return {"risk_score": 84, "risk_tier": "low", "explanation": "ANA nonstop, excellent on-time record."}
        if "JL" in flight_number:
            return {"risk_score": 80, "risk_tier": "low", "explanation": "JAL direct, strong seasonal reliability."}
        if "UA" in flight_number:
            return {"risk_score": 72, "risk_tier": "moderate", "explanation": "UA nonstop, occasional delays on SFO-NRT."}
        if stops == 0:
            return {"risk_score": 74, "risk_tier": "moderate", "explanation": "Direct flight with moderate on-time performance."}
        if stops == 1:
            return {"risk_score": 62, "risk_tier": "moderate", "explanation": "One connection adds delay risk."}
        return {"risk_score": 55, "risk_tier": "moderate", "explanation": "Multiple connections increase disruption risk."}


def _default_offers() -> list[dict[str, Any]]:
    return [
        {
            "id": "cheap",
            "price": {"total": "720.00", "currency": "USD"},
            "itineraries": [
                {
                    "duration": "PT12H50M",
                    "segments": [
                        {
                            "carrierCode": "UA",
                            "number": "837",
                            "departure": {"iataCode": "SFO", "at": "2026-10-15T11:30:00"},
                            "arrival": {"iataCode": "NRT", "at": "2026-10-16T15:10:00"},
                        }
                    ],
                }
            ],
            "validatingAirlineCodes": ["UA"],
        },
        {
            "id": "recommended",
            "price": {"total": "890.00", "currency": "USD"},
            "itineraries": [
                {
                    "duration": "PT11H15M",
                    "segments": [
                        {
                            "carrierCode": "NH",
                            "number": "107",
                            "departure": {"iataCode": "SFO", "at": "2026-10-15T01:20:00"},
                            "arrival": {"iataCode": "HND", "at": "2026-10-16T05:35:00"},
                        }
                    ],
                }
            ],
            "validatingAirlineCodes": ["NH"],
        },
        {
            "id": "premium",
            "price": {"total": "1350.00", "currency": "USD"},
            "itineraries": [
                {
                    "duration": "PT10H55M",
                    "segments": [
                        {
                            "carrierCode": "JL",
                            "number": "1",
                            "departure": {"iataCode": "SFO", "at": "2026-10-15T12:20:00"},
                            "arrival": {"iataCode": "HND", "at": "2026-10-16T15:15:00"},
                        }
                    ],
                }
            ],
            "validatingAirlineCodes": ["JL"],
        },
    ]


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class RiskRequest(BaseModel):
    flight_number: str
    departure_datetime: str
    origin_iata: str
    destination_iata: str
    airline_iata: str
    stops: int = 0
    connection_minutes: int = 0
    duration_minutes: int = 0


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/search")
def flights_search(
    origin: str = Query(..., description="Origin IATA airport code", examples=["SFO"]),
    destination: str = Query(..., description="Destination IATA airport code", examples=["TYO"]),
    date: str = Query(..., description="Departure date YYYY-MM-DD", examples=["2026-10-15"]),
    adults: int = Query(1, description="Number of adult passengers"),
    return_date: str | None = Query(None, description="Optional return date YYYY-MM-DD"),
    max_budget_usd: float | None = Query(None, description="Maximum budget per person in USD"),
    preferred_airlines: str | None = Query(
        None, description="Comma-separated airline codes, e.g. NH,UA,JL"
    ),
    max_duration_hours: float | None = Query(None, description="Maximum flight duration in hours"),
) -> dict[str, Any]:
    """Search for flight options between two airports on a given date."""
    airlines = [a.strip() for a in preferred_airlines.split(",")] if preferred_airlines else None

    # Use fake client when no live credentials are configured.
    # Replace FakeAmadeusClient with a real Amadeus client when
    # AMADEUS_CLIENT_ID / AMADEUS_CLIENT_SECRET are set in settings.
    amadeus_client = FakeAmadeusClient()
    scorer = FakeRiskScorer()

    result = search_flights(
        origin=origin,
        destination=destination,
        departure_date=date,
        return_date=return_date,
        adults=adults,
        max_budget_usd=max_budget_usd,
        preferred_airlines=airlines,
        max_duration_hours=max_duration_hours,
        amadeus_client=amadeus_client,
        risk_scorer=scorer,
    )
    return result


@router.get("/risk")
def flights_risk(
    flight_number: str = Query(..., description="Flight number, e.g. NH107"),
    departure_datetime: str = Query(
        ..., description="ISO-8601 departure datetime", examples=["2026-10-15T01:20:00"]
    ),
    origin_iata: str = Query(..., description="Origin IATA", examples=["SFO"]),
    destination_iata: str = Query(..., description="Destination IATA", examples=["HND"]),
    airline_iata: str = Query(..., description="Airline IATA code", examples=["NH"]),
    stops: int = Query(0, description="Number of stops"),
    connection_minutes: int = Query(0, description="Total connection time in minutes"),
    duration_minutes: int = Query(0, description="Total flight duration in minutes"),
) -> dict[str, Any]:
    """Score the disruption risk for a specific flight."""
    flight = {
        "flight_number": flight_number,
        "scheduled_departure_local": departure_datetime,
        "origin_iata": origin_iata,
        "destination_iata": destination_iata,
        "airline_iata": airline_iata,
        "stops": stops,
        "connection_minutes": connection_minutes,
        "duration_minutes": duration_minutes,
    }

    # For demo / test: use the fake scorer (no real DB required).
    # Replace with real collections when MongoDB is connected.
    fake_fp = {"on_time_pct": 0.82, "departure_time_reliability": {"morning": 80, "afternoon": 75}}
    fake_ar = {"iata": airline_iata, "skytrax_rating": 4}

    class _FakeCollection:
        def find_one(self, *_args, **_kwargs):
            return None

    class _FakeFpCollection:
        def find_one(self, *_args, **_kwargs):
            return fake_fp

    class _FakeArCollection:
        def find_one(self, *_args, **_kwargs):
            return fake_ar

    result = score_flight_risk(
        flight=flight,
        flight_performance_collection=_FakeFpCollection(),
        airline_ratings_collection=_FakeArCollection(),
    )
    return result