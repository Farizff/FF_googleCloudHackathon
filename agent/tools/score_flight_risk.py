from datetime import datetime
from typing import Any


INVALID_DEPARTURE_DATETIME = "INVALID_DEPARTURE_DATETIME"
TIME_SLOT_FALLBACKS = {
    "early_morning": 88.0,
    "morning": 82.0,
    "afternoon": 70.0,
    "evening": 65.0,
}
WEIGHTS = {
    "on_time_performance": 0.35,
    "airline_reliability": 0.25,
    "time_of_day_reliability": 0.20,
    "seasonal_adjustment": 0.10,
    "connection_adequacy": 0.10,
}


def score_flight_risk(
    flight: dict[str, Any],
    flight_performance_collection: Any,
    airline_ratings_collection: Any,
    amadeus_delay_prediction: float | None = None,
) -> dict[str, Any]:
    """Score flight risk using deterministic PRD 6.4 weighted dimensions."""
    departure_datetime_raw = flight.get("scheduled_departure_local")
    departure_datetime = _parse_departure_datetime(departure_datetime_raw)
    if departure_datetime is None:
        return _error(
            INVALID_DEPARTURE_DATETIME,
            f"Invalid scheduled_departure_local '{departure_datetime_raw}'.",
        )

    route_performance = _find_route_performance(flight, flight_performance_collection)
    airline_rating = airline_ratings_collection.find_one({"iata": flight.get("airline_iata")})
    slot = _time_slot(departure_datetime.hour)

    dimensions = {
        "on_time_performance": _on_time_score(route_performance, amadeus_delay_prediction),
        "airline_reliability": _airline_score(airline_rating),
        "time_of_day_reliability": _time_of_day_score(route_performance, slot),
        "seasonal_adjustment": _seasonal_score(route_performance, departure_datetime.month),
        "connection_adequacy": _connection_score(flight),
    }
    risk_score = round(sum(dimensions[name] * weight for name, weight in WEIGHTS.items()))

    return {
        "risk_score": risk_score,
        "risk_tier": _risk_tier(risk_score),
        "dimensions": {name: round(value, 2) for name, value in dimensions.items()},
        "explanation": _explanation(risk_score, dimensions),
    }


def _parse_departure_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _find_route_performance(flight: dict[str, Any], collection: Any) -> dict[str, Any] | None:
    route_id = flight.get("route_id")
    if route_id:
        return collection.find_one({"route_id": route_id})

    route_key = flight.get("route_key")
    airline_iata = flight.get("airline_iata")
    flight_number = flight.get("flight_number")
    if route_key and airline_iata and flight_number:
        return collection.find_one(
            {
                "route_key": route_key,
                "airline_iata": airline_iata,
                "flight_number": flight_number,
            }
        )
    return None


def _on_time_score(route_performance: dict[str, Any] | None, amadeus_delay_prediction: float | None) -> float:
    if route_performance is not None and route_performance.get("on_time_pct") is not None:
        return float(route_performance["on_time_pct"]) * 100
    if amadeus_delay_prediction is not None:
        return float(amadeus_delay_prediction) * 100
    return 75.0


def _airline_score(airline_rating: dict[str, Any] | None) -> float:
    if airline_rating is None or airline_rating.get("skytrax_rating") is None:
        return 60.0
    return float(airline_rating["skytrax_rating"]) / 5 * 100


def _time_slot(hour: int) -> str:
    if 5 <= hour < 8:
        return "early_morning"
    if 8 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour <= 23:
        return "evening"
    return "early_morning"


def _time_of_day_score(route_performance: dict[str, Any] | None, slot: str) -> float:
    if route_performance is not None:
        reliabilities = route_performance.get("departure_time_reliability") or {}
        if reliabilities.get(slot) is not None:
            return float(reliabilities[slot])
    return TIME_SLOT_FALLBACKS[slot]


def _seasonal_score(route_performance: dict[str, Any] | None, departure_month: int) -> float:
    if route_performance is None:
        return 100.0

    seasonal_risk = route_performance.get("seasonal_risk") or {}
    risk = seasonal_risk.get(f"{departure_month:02d}") or seasonal_risk.get(departure_month)
    if risk is None:
        return 100.0

    multiplier = risk.get("risk_multiplier") if isinstance(risk, dict) else risk
    if multiplier is None:
        return 100.0
    return min(100.0, (1 / float(multiplier)) * 100)


def _connection_score(flight: dict[str, Any]) -> float:
    stops = int(flight.get("stops") or 0)
    if stops == 0:
        return 100.0

    connection_minutes = float(flight.get("connection_minutes") or 0)
    if stops == 1 and connection_minutes > 90:
        return 80.0
    if stops == 1 and 60 <= connection_minutes <= 90:
        return 60.0
    return 30.0


def _risk_tier(score: int) -> str:
    if score >= 75:
        return "low"
    if score >= 50:
        return "moderate"
    return "high"


def _explanation(risk_score: int, dimensions: dict[str, float]) -> str:
    return (
        f"Flight risk is {risk_score}/100 ({_risk_tier(risk_score)}). "
        f"On-time performance contributes {dimensions['on_time_performance']:.0f}, "
        f"airline reliability {dimensions['airline_reliability']:.0f}, "
        f"time-of-day reliability {dimensions['time_of_day_reliability']:.0f}, "
        f"seasonal adjustment {dimensions['seasonal_adjustment']:.0f}, and "
        f"connection adequacy {dimensions['connection_adequacy']:.0f}."
    )


def _error(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}
