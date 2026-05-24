import re
from typing import Any


PRICE_NOTE = "Prices are estimates until booking is confirmed at the airline site."
NO_FLIGHT_OPTIONS = "NO_FLIGHT_OPTIONS"
OPTION_TIERS = ["budget", "recommended", "premium"]


def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None,
    adults: int,
    max_budget_usd: float | None,
    preferred_airlines: list[str] | None,
    max_duration_hours: float | None,
    amadeus_client: Any,
    risk_scorer: Any | None = None,
    max_results: int = 20,
) -> dict[str, Any]:
    """Search Amadeus-shaped flight offers and return labelled Bounce options."""
    raw_offers = amadeus_client.flight_offers_search(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        adults=adults,
        max=max_results,
    )
    flights = [_normalize_offer(offer) for offer in raw_offers if isinstance(offer, dict)]
    flights = [flight for flight in flights if flight is not None]
    flights = _filter_flights(flights, max_budget_usd, preferred_airlines or [], max_duration_hours)
    if not flights:
        return _error(NO_FLIGHT_OPTIONS, "No flight options matched the request.")

    selected = _select_options(flights)
    tiers = _tiers_for_count(len(selected))
    options = []
    for tier, flight in zip(tiers, selected):
        option = {"tier": tier, **flight, "price_note": PRICE_NOTE}
        if risk_scorer is not None:
            risk = risk_scorer.score(flight)
            if isinstance(risk, dict) and "error" not in risk:
                option.update(
                    {
                        "risk_score": risk.get("risk_score"),
                        "risk_tier": risk.get("risk_tier"),
                        "risk_explanation": risk.get("explanation"),
                    }
                )
        options.append(option)

    result: dict[str, Any] = {"options": options}
    if len(options) < 3:
        suffix = "option was" if len(options) == 1 else "options were"
        result["note"] = f"Only {len(options)} flight {suffix} available."
    return result


def _normalize_offer(offer: dict[str, Any]) -> dict[str, Any] | None:
    if offer.get("flight_number"):
        return _normalize_flat_offer(offer)
    return _normalize_amadeus_offer(offer)


def _normalize_flat_offer(offer: dict[str, Any]) -> dict[str, Any]:
    return {
        "flight_number": str(offer.get("flight_number")),
        "airline_iata": offer.get("airline_iata"),
        "origin_iata": offer.get("origin_iata"),
        "destination_iata": offer.get("destination_iata"),
        "departure_datetime": offer.get("departure_datetime"),
        "arrival_datetime": offer.get("arrival_datetime"),
        "price_usd": float(offer.get("price_usd") or 0),
        "duration_minutes": int(offer.get("duration_minutes") or 0),
        "stops": int(offer.get("stops") or 0),
        "connection_minutes": int(offer.get("connection_minutes") or 0),
    }


def _normalize_amadeus_offer(offer: dict[str, Any]) -> dict[str, Any] | None:
    itineraries = offer.get("itineraries") or []
    if not itineraries:
        return None
    itinerary = itineraries[0]
    segments = itinerary.get("segments") or []
    if not segments:
        return None

    first = segments[0]
    last = segments[-1]
    airline_iata = first.get("carrierCode") or (offer.get("validatingAirlineCodes") or [None])[0]
    number = first.get("number")
    flight_number = f"{airline_iata}{number}" if airline_iata and number else str(offer.get("id"))
    price = offer.get("price") or {}
    duration_minutes = _parse_iso_duration_minutes(itinerary.get("duration"))
    stops = max(0, len(segments) - 1)

    return {
        "flight_number": flight_number,
        "airline_iata": airline_iata,
        "origin_iata": (first.get("departure") or {}).get("iataCode"),
        "destination_iata": (last.get("arrival") or {}).get("iataCode"),
        "departure_datetime": (first.get("departure") or {}).get("at"),
        "arrival_datetime": (last.get("arrival") or {}).get("at"),
        "price_usd": float(price.get("total") or 0),
        "duration_minutes": duration_minutes,
        "stops": stops,
        "connection_minutes": _connection_minutes(segments),
    }


def _parse_iso_duration_minutes(value: Any) -> int:
    if not isinstance(value, str):
        return 0
    match = re.fullmatch(r"P(?:\d+D)?T(?:(\d+)H)?(?:(\d+)M)?", value)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    return hours * 60 + minutes


def _connection_minutes(segments: list[dict[str, Any]]) -> int:
    if len(segments) <= 1:
        return 0
    # Amadeus offer snippets do not always include enough timezone-safe context;
    # leave precise layover computation to normalized/seeded data when provided.
    return 0


def _filter_flights(
    flights: list[dict[str, Any]],
    max_budget_usd: float | None,
    preferred_airlines: list[str],
    max_duration_hours: float | None,
) -> list[dict[str, Any]]:
    filtered = list(flights)
    if max_budget_usd is not None:
        filtered = [flight for flight in filtered if flight["price_usd"] <= float(max_budget_usd)]
    if max_duration_hours is not None:
        max_minutes = float(max_duration_hours) * 60
        filtered = [flight for flight in filtered if flight["duration_minutes"] <= max_minutes]
    if preferred_airlines:
        preferred = {airline.upper() for airline in preferred_airlines}
        preferred_matches = [flight for flight in filtered if str(flight.get("airline_iata", "")).upper() in preferred]
        if preferred_matches:
            filtered = preferred_matches
    return filtered


def _select_options(flights: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(flights) <= 2:
        return sorted(flights, key=lambda flight: (_balance_score(flight, flights), flight["price_usd"]))

    budget = min(flights, key=lambda flight: (flight["price_usd"], flight["duration_minutes"]))
    premium = min(flights, key=lambda flight: (flight["duration_minutes"], flight["price_usd"]))
    remaining = [flight for flight in flights if flight is not budget and flight is not premium]
    recommended = min(remaining or flights, key=lambda flight: (_balance_score(flight, flights), flight["stops"]))

    selected = []
    for flight in (budget, recommended, premium):
        if flight not in selected:
            selected.append(flight)
    return selected[:3]


def _balance_score(flight: dict[str, Any], flights: list[dict[str, Any]]) -> float:
    max_price = max((candidate["price_usd"] for candidate in flights), default=1) or 1
    max_duration = max((candidate["duration_minutes"] for candidate in flights), default=1) or 1
    return (flight["price_usd"] / max_price * 0.45) + (flight["duration_minutes"] / max_duration * 0.55)


def _tiers_for_count(count: int) -> list[str]:
    if count == 1:
        return ["recommended"]
    if count == 2:
        return ["budget", "recommended"]
    return OPTION_TIERS


def _error(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}
