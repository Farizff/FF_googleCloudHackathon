from agent.tools.search_flights import search_flights


class FakeAmadeusClient:
    def __init__(self, offers):
        self.offers = offers
        self.calls = []

    def flight_offers_search(self, **kwargs):
        self.calls.append(kwargs)
        return list(self.offers)


class FakeRiskScorer:
    def __init__(self):
        self.calls = []

    def score(self, flight):
        self.calls.append(flight)
        if flight["flight_number"] == "NH107":
            return {"risk_score": 86, "risk_tier": "low", "explanation": "Low risk direct flight."}
        if flight["flight_number"] == "UA837":
            return {"risk_score": 80, "risk_tier": "low", "explanation": "Low risk nonstop option."}
        return {"risk_score": 64, "risk_tier": "moderate", "explanation": "Moderate connection risk."}


def test_search_flights_calls_amadeus_and_returns_three_labelled_options():
    amadeus = FakeAmadeusClient(
        [
            {
                "id": "cheap",
                "price": {"total": "690.00", "currency": "USD"},
                "itineraries": [
                    {
                        "duration": "PT13H40M",
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
                "id": "balanced",
                "price": {"total": "840.00", "currency": "USD"},
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
                "price": {"total": "1280.00", "currency": "USD"},
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
    )
    scorer = FakeRiskScorer()

    result = search_flights(
        origin="SFO",
        destination="TYO",
        departure_date="2026-10-15",
        return_date="2026-10-25",
        adults=2,
        max_budget_usd=1500,
        preferred_airlines=["NH", "UA", "JL"],
        max_duration_hours=15,
        amadeus_client=amadeus,
        risk_scorer=scorer,
    )

    assert amadeus.calls == [
        {
            "origin": "SFO",
            "destination": "TYO",
            "departure_date": "2026-10-15",
            "return_date": "2026-10-25",
            "adults": 2,
            "max": 20,
        }
    ]
    assert [option["tier"] for option in result["options"]] == ["budget", "recommended", "premium"]
    assert [option["flight_number"] for option in result["options"]] == ["UA837", "NH107", "JL1"]
    assert result["options"][1]["risk_score"] == 86
    assert result["options"][1]["risk_tier"] == "low"
    assert result["options"][1]["price_note"] == "Prices are estimates until booking is confirmed at the airline site."
    assert len(scorer.calls) == 3


def test_search_flights_filters_budget_duration_and_preferred_airlines_when_possible():
    amadeus = FakeAmadeusClient(
        [
            _simple_offer("AA", "100", 500, 700, "2026-10-15T08:00:00", "2026-10-15T19:40:00"),
            _simple_offer("NH", "107", 900, 680, "2026-10-15T01:20:00", "2026-10-15T12:40:00"),
            _simple_offer("UA", "837", 1100, 700, "2026-10-15T11:30:00", "2026-10-15T23:10:00"),
            _simple_offer("DL", "9", 2200, 650, "2026-10-15T10:00:00", "2026-10-15T20:50:00"),
        ]
    )

    result = search_flights(
        "SFO",
        "TYO",
        "2026-10-15",
        "2026-10-25",
        1,
        max_budget_usd=1200,
        preferred_airlines=["NH", "UA"],
        max_duration_hours=12,
        amadeus_client=amadeus,
    )

    assert [option["flight_number"] for option in result["options"]] == ["NH107", "UA837"]
    assert [option["tier"] for option in result["options"]] == ["budget", "recommended"]
    assert all(option["airline_iata"] in {"NH", "UA"} for option in result["options"])


def test_search_flights_normalizes_flat_offer_shape_and_connection_fields():
    amadeus = FakeAmadeusClient(
        [
            {
                "flight_number": "UA79",
                "airline_iata": "UA",
                "origin_iata": "JFK",
                "destination_iata": "NRT",
                "departure_datetime": "2026-10-15T11:15:00",
                "arrival_datetime": "2026-10-16T14:20:00",
                "price_usd": 980,
                "duration_minutes": 965,
                "stops": 1,
                "connection_minutes": 105,
            }
        ]
    )

    result = search_flights("JFK", "NRT", "2026-10-15", "2026-10-25", 1, None, [], None, amadeus)

    assert result == {
        "options": [
            {
                "tier": "recommended",
                "flight_number": "UA79",
                "airline_iata": "UA",
                "origin_iata": "JFK",
                "destination_iata": "NRT",
                "departure_datetime": "2026-10-15T11:15:00",
                "arrival_datetime": "2026-10-16T14:20:00",
                "price_usd": 980.0,
                "duration_minutes": 965,
                "stops": 1,
                "connection_minutes": 105,
                "price_note": "Prices are estimates until booking is confirmed at the airline site.",
            }
        ],
        "note": "Only 1 flight option was available.",
    }


def test_search_flights_returns_standard_error_when_amadeus_has_no_options():
    result = search_flights("SFO", "TYO", "2026-10-15", None, 1, None, [], None, FakeAmadeusClient([]))

    assert result == {"error": {"code": "NO_FLIGHT_OPTIONS", "message": "No flight options matched the request."}}


def _simple_offer(airline, number, price, duration, departure, arrival):
    return {
        "flight_number": f"{airline}{number}",
        "airline_iata": airline,
        "origin_iata": "SFO",
        "destination_iata": "TYO",
        "departure_datetime": departure,
        "arrival_datetime": arrival,
        "price_usd": price,
        "duration_minutes": duration,
        "stops": 0,
        "connection_minutes": 0,
    }
