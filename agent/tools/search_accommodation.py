from typing import Any
from urllib.parse import urlparse


PLACE_TYPES = ["lodging"]
PRICE_NOTE = "Final price confirmed at booking site."
OPTION_TIERS = ["budget", "recommended", "premium"]
CATEGORY_FOR_TIER = {
    "budget": "budget",
    "recommended": "mid_range",
    "premium": "premium",
}
DEFAULT_PRICE_USD = {
    "budget": 80,
    "mid_range": 180,
    "premium": 350,
}
APPROVED_BOOKING_DOMAINS = [
    "booking.com",
    "expedia.com",
    "hotels.com",
    "agoda.com",
    "airbnb.com",
    "google.com",
]


def search_accommodation(
    city: str,
    check_in: str,
    check_out: str,
    group_size: int,
    budget_tier: str,
    places_client: Any,
    price_estimator: Any | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Return accommodation options labelled budget/recommended/premium.

    The external integrations are dependency-injected so tests can use tiny
    deterministic fakes. `places_client` is expected to expose `hotel_search`;
    `price_estimator`, when present, may expose `estimate_price_per_night_usd`.
    """
    del budget_tier  # Future ranking hint; fixed PRD labels are always returned.

    raw_hotels = places_client.hotel_search(
        city=city,
        check_in=check_in,
        check_out=check_out,
        group_size=group_size,
        place_types=PLACE_TYPES,
        limit=limit,
    )
    hotels = [_normalize_hotel(hotel) for hotel in raw_hotels if isinstance(hotel, dict)]
    if not hotels:
        return {"options": [], "note": "No accommodation options were available."}

    selected = _select_options(hotels)
    tiers = _tiers_for_count(len(selected))
    options = []
    for tier, hotel in zip(tiers, selected):
        category = hotel["category"]
        options.append(
            {
                "tier": tier,
                "place_id": hotel["place_id"],
                "name": hotel["name"],
                "address": hotel["address"],
                "coordinates": hotel["coordinates"],
                "rating": hotel["rating"],
                "types": hotel["types"],
                "category": category,
                "price_per_night_usd": _estimate_price(
                    city=city,
                    category=category,
                    group_size=group_size,
                    check_in=check_in,
                    check_out=check_out,
                    price_estimator=price_estimator,
                ),
                "price_note": PRICE_NOTE,
                "booking_url": _safe_booking_url(hotel["booking_url"]),
            }
        )

    result: dict[str, Any] = {"options": options}
    if len(options) < 3:
        suffix = "option was" if len(options) == 1 else "options were"
        result["note"] = f"Only {len(options)} accommodation {suffix} available."
    return result


def _normalize_hotel(hotel: dict[str, Any]) -> dict[str, Any]:
    return {
        "place_id": hotel.get("place_id"),
        "name": hotel.get("name"),
        "address": hotel.get("address") or hotel.get("formatted_address") or hotel.get("vicinity"),
        "coordinates": hotel.get("coordinates") or _coordinates_from_geometry(hotel.get("geometry")),
        "rating": hotel.get("rating"),
        "types": hotel.get("types", []),
        "category": _category(hotel),
        "booking_url": hotel.get("booking_url") or hotel.get("url") or hotel.get("website"),
        "price_level": hotel.get("price_level"),
    }


def _coordinates_from_geometry(geometry: Any) -> dict[str, float] | None:
    if not isinstance(geometry, dict):
        return None
    location = geometry.get("location")
    if not isinstance(location, dict):
        return None
    if "lat" not in location or "lng" not in location:
        return None
    return {"lat": location["lat"], "lng": location["lng"]}


def _category(hotel: dict[str, Any]) -> str:
    explicit = hotel.get("category") or hotel.get("hotel_category")
    if explicit in {"budget", "mid_range", "premium"}:
        return explicit

    price_level = hotel.get("price_level")
    if price_level is not None:
        try:
            level = int(price_level)
        except (TypeError, ValueError):
            level = 2
        if level <= 1:
            return "budget"
        if level >= 4:
            return "premium"
        return "mid_range"

    rating = float(hotel.get("rating") or 0)
    if rating >= 4.7:
        return "premium"
    if rating <= 4.0:
        return "budget"
    return "mid_range"


def _select_options(hotels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(hotels) == 1:
        return hotels

    selected: list[dict[str, Any]] = []
    for category in ("budget", "mid_range", "premium"):
        candidates = [hotel for hotel in hotels if hotel["category"] == category]
        if candidates:
            selected.append(max(candidates, key=lambda hotel: hotel.get("rating") or 0))

    if len(selected) >= 3:
        return selected[:3]

    for hotel in sorted(hotels, key=lambda item: item.get("rating") or 0, reverse=True):
        if hotel not in selected:
            selected.append(hotel)
        if len(selected) == min(3, len(hotels)):
            break
    return selected


def _tiers_for_count(count: int) -> list[str]:
    if count == 1:
        return ["recommended"]
    if count == 2:
        return ["budget", "recommended"]
    return OPTION_TIERS


def _estimate_price(
    city: str,
    category: str,
    group_size: int,
    check_in: str,
    check_out: str,
    price_estimator: Any | None,
) -> int:
    if price_estimator is not None:
        estimate = price_estimator.estimate_price_per_night_usd(
            city=city,
            category=category,
            group_size=group_size,
            check_in=check_in,
            check_out=check_out,
        )
        return int(round(float(estimate)))
    return DEFAULT_PRICE_USD[category]


def _safe_booking_url(url: Any) -> str | None:
    if not url:
        return None
    parsed = urlparse(str(url))
    domain = parsed.netloc.lower().removeprefix("www.")
    if parsed.scheme not in {"http", "https"}:
        return None
    if any(domain.endswith(approved) for approved in APPROVED_BOOKING_DOMAINS):
        return str(url)
    return None
