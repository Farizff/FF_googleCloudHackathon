from math import ceil
from typing import Any


OPTION_TIERS = ["budget", "recommended", "premium"]
TAXI_CAPACITY = 4
LARGE_GROUP_THRESHOLD = 6


def get_multi_modal_transport(
    origin: Any,
    destination: Any,
    date: str,
    group_size: int,
    rome2rio_client: Any,
) -> dict[str, list[dict[str, Any]]]:
    """Return up to 3 Rome2Rio transport options labelled for Bounce rec-cards."""
    response = rome2rio_client.search(
        origin=origin,
        destination=destination,
        date=date,
        group_size=group_size,
    )
    routes = _dedupe_by_mode(_normalize_routes(response))
    if not routes:
        return {"options": []}

    selected = _select_three(routes)
    note = _group_transport_note(group_size)
    labelled = []
    tiers = _tiers_for_count(len(selected))
    for tier, option in zip(tiers, selected):
        labelled_option = {"tier": tier, **option}
        if note is not None:
            labelled_option["group_transport_note"] = note
        labelled.append(labelled_option)
    return {"options": labelled}


def _normalize_routes(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, dict):
        raw_routes = response.get("routes") or response.get("options") or []
    elif isinstance(response, list):
        raw_routes = response
    else:
        raw_routes = []

    normalized = []
    for route in raw_routes:
        if not isinstance(route, dict):
            continue
        normalized.append(_normalize_route(route))
    return normalized


def _normalize_route(route: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": _mode(route),
        "duration_minutes": _duration_minutes(route),
        "estimated_cost_usd": _estimated_cost_usd(route),
        "transfers": _transfers(route),
        "summary": route.get("summary") or route.get("name") or _mode(route),
    }


def _mode(route: dict[str, Any]) -> str:
    if route.get("mode"):
        return str(route["mode"])
    segments = route.get("segments") or []
    kinds = []
    for segment in segments:
        if isinstance(segment, dict):
            kind = segment.get("kind") or segment.get("mode")
            if kind:
                kinds.append(str(kind))
    return "+".join(kinds) if kinds else "unknown"


def _duration_minutes(route: dict[str, Any]) -> int:
    if route.get("duration_minutes") is not None:
        return int(route["duration_minutes"])
    duration = route.get("duration")
    if isinstance(duration, dict):
        duration = duration.get("value")
    return round(float(duration or 0) / 60)


def _estimated_cost_usd(route: dict[str, Any]) -> float:
    if route.get("estimated_cost_usd") is not None:
        return float(route["estimated_cost_usd"])
    prices = route.get("indicativePrices") or route.get("indicative_prices") or []
    for price in prices:
        if isinstance(price, dict) and price.get("price") is not None:
            return float(price["price"])
    if route.get("price") is not None:
        return float(route["price"])
    return 0.0


def _transfers(route: dict[str, Any]) -> int:
    if route.get("transfers") is not None:
        return int(route["transfers"])
    segments = route.get("segments") or []
    return max(0, len(segments) - 1)


def _dedupe_by_mode(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best_by_mode: dict[str, dict[str, Any]] = {}
    for route in routes:
        mode = route["mode"]
        current = best_by_mode.get(mode)
        if current is None or _balance_score(route, routes) < _balance_score(current, routes):
            best_by_mode[mode] = route
    return list(best_by_mode.values())


def _select_three(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(routes) <= 2:
        return sorted(routes, key=lambda route: (_balance_score(route, routes), route["duration_minutes"]))

    budget = min(routes, key=lambda route: (route["estimated_cost_usd"], route["duration_minutes"]))
    premium = min(routes, key=lambda route: (route["duration_minutes"], route["estimated_cost_usd"]))
    remaining = [route for route in routes if route is not budget and route is not premium]
    recommended = min(remaining or routes, key=lambda route: (_balance_score(route, routes), route["transfers"]))

    selected = []
    for route in (budget, recommended, premium):
        if route not in selected:
            selected.append(route)
    return selected[:3]


def _balance_score(route: dict[str, Any], routes: list[dict[str, Any]]) -> float:
    max_duration = max((candidate["duration_minutes"] for candidate in routes), default=1) or 1
    max_cost = max((candidate["estimated_cost_usd"] for candidate in routes), default=1) or 1
    return (route["duration_minutes"] / max_duration * 0.55) + (
        route["estimated_cost_usd"] / max_cost * 0.45
    )


def _tiers_for_count(count: int) -> list[str]:
    if count == 1:
        return ["recommended"]
    if count == 2:
        return ["budget", "recommended"]
    return OPTION_TIERS


def _group_transport_note(group_size: int) -> str | None:
    if group_size <= LARGE_GROUP_THRESHOLD:
        return None
    taxi_count = ceil(group_size / TAXI_CAPACITY)
    return f"{group_size} people: chartered minibus (~$80) or {taxi_count} taxis (~$95 total)."
