from typing import Any


DEFAULT_PLACE_TYPES = ["tourist_attraction"]
CATEGORY_PLACE_TYPES = {
    "museum": ["museum", "tourist_attraction"],
    "temple": ["place_of_worship", "tourist_attraction"],
    "restaurant": ["restaurant", "food"],
    "market": ["market", "food", "tourist_attraction"],
    "park": ["park", "tourist_attraction"],
    "shopping_street": ["shopping_mall", "store", "tourist_attraction"],
    "observation_deck": ["tourist_attraction", "point_of_interest"],
    "meeting_point": ["point_of_interest", "transit_station"],
}

FALLBACK_ENRICHMENT = {
    "category_pattern": "general",
    "physical_intensity": "medium",
    "estimated_duration_minutes": 90,
    "crowd_peak_weekday": {"start": "11:00", "end": "15:00"},
    "crowd_peak_weekend": {"start": "10:00", "end": "16:00"},
    "customs": {"behavioural_notes": "follow posted venue guidance"},
    "dietary_relevance": "none",
    "child_friendly": True,
    "elderly_friendly": True,
    "wheelchair_accessibility": "varies",
}

FOOD_TYPES = {"restaurant", "food", "meal_takeaway", "cafe", "bakery", "bar"}
GENERIC_PLACE_TYPES = {"tourist_attraction", "point_of_interest", "establishment", "food"}


def search_venues(
    city: str,
    destination_country: str,
    date: str,
    group_dietary_restrictions: list[str],
    group_interests: list[str],
    mobility_max: str,
    group_size: int,
    places_client: Any,
    enrichment_collection: Any,
    categories: list[str] | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Search and enrich venues using injected Places and enrichment dependencies."""
    del group_interests, group_size  # Future scoring inputs; keep contract explicit.

    place_types = _place_types_for_categories(categories or [])
    place_results = places_client.nearby_search(
        city=city,
        destination_country=destination_country,
        date=date,
        place_types=place_types,
        limit=20,
    )
    enrichments = list(enrichment_collection.find({}))

    merged_venues = []
    for place in place_results:
        enrichment = _best_enrichment_for_place(place, enrichments)
        venue = _merge_place_and_enrichment(place, enrichment)
        if _is_mobility_compatible(venue, mobility_max) and _is_dietary_compatible(
            venue, group_dietary_restrictions
        ):
            merged_venues.append(venue)

    sorted_venues = sorted(merged_venues, key=lambda venue: venue.get("rating") or 0, reverse=True)
    return {"venues": sorted_venues[:limit], "total_found": len(sorted_venues)}


def _place_types_for_categories(categories: list[str]) -> list[str]:
    place_types: list[str] = []
    for category in categories:
        place_types.extend(CATEGORY_PLACE_TYPES.get(category, [category]))
    if not place_types:
        place_types.extend(DEFAULT_PLACE_TYPES)
    return sorted(set(place_types))


def _best_enrichment_for_place(place: dict[str, Any], enrichments: list[dict[str, Any]]) -> dict[str, Any]:
    place_types = set(place.get("types", []))
    scored_matches = []
    for index, enrichment in enumerate(enrichments):
        enrichment_types = set(enrichment.get("google_place_types", []))
        overlap = place_types.intersection(enrichment_types)
        if overlap:
            specific_overlap = overlap - GENERIC_PLACE_TYPES
            scored_matches.append((len(specific_overlap), len(overlap), -index, enrichment))

    if not scored_matches:
        return FALLBACK_ENRICHMENT
    return max(scored_matches, key=lambda match: match[:3])[3]


def _merge_place_and_enrichment(place: dict[str, Any], enrichment: dict[str, Any]) -> dict[str, Any]:
    return {
        "place_id": place.get("place_id"),
        "name": place.get("name"),
        "types": place.get("types", []),
        "rating": place.get("rating"),
        "coordinates": place.get("coordinates"),
        "opening_hours": place.get("opening_hours"),
        "photos": place.get("photos", []),
        "dietary_supported": place.get("dietary_supported", []),
        "category_pattern": enrichment["category_pattern"],
        "physical_intensity": enrichment["physical_intensity"],
        "estimated_duration_minutes": enrichment["estimated_duration_minutes"],
        "crowd_peak_weekday": enrichment["crowd_peak_weekday"],
        "crowd_peak_weekend": enrichment["crowd_peak_weekend"],
        "customs": enrichment["customs"],
        "dietary_relevance": enrichment["dietary_relevance"],
        "child_friendly": enrichment["child_friendly"],
        "elderly_friendly": enrichment["elderly_friendly"],
        "wheelchair_accessibility": enrichment["wheelchair_accessibility"],
    }


def _is_mobility_compatible(venue: dict[str, Any], mobility_max: str) -> bool:
    if mobility_max == "wheelchair":
        return venue["wheelchair_accessibility"] == "full"
    if mobility_max == "limited":
        return venue["physical_intensity"] != "high" and venue["wheelchair_accessibility"] in {
            "full",
            "partial",
            "varies",
        }
    return True


def _is_dietary_compatible(venue: dict[str, Any], restrictions: list[str]) -> bool:
    required = {restriction.lower() for restriction in restrictions if restriction}
    if not required:
        return True

    supported = {diet.lower() for diet in venue.get("dietary_supported", [])}
    place_types = set(venue.get("types", []))
    is_food_venue = bool(place_types.intersection(FOOD_TYPES)) or venue["dietary_relevance"] == "high"
    if not is_food_venue:
        return True
    return required.issubset(supported)
