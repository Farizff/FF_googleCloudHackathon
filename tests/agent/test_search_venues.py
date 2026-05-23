from agent.tools.search_venues import search_venues


class FakePlacesClient:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def nearby_search(self, **kwargs):
        self.calls.append(kwargs)
        return self.results


class FakeVenueEnrichmentCollection:
    def __init__(self, records):
        self.records = records
        self.queries = []

    def find(self, query):
        self.queries.append(query)
        return list(self.records)


def test_search_venues_merges_places_with_enrichment_sorts_by_rating_and_limits():
    """Places results should be enriched, sorted by rating, and limited deterministically."""
    places = FakePlacesClient(
        [
            {
                "place_id": "place_sensoji",
                "name": "Senso-ji",
                "types": ["place_of_worship", "tourist_attraction"],
                "rating": 4.5,
                "coordinates": {"lat": 35.7148, "lng": 139.7967},
                "opening_hours": {"open_now": True},
                "photos": ["sensoji.jpg"],
            },
            {
                "place_id": "place_mori",
                "name": "Mori Art Museum",
                "types": ["museum", "tourist_attraction"],
                "rating": 4.7,
                "coordinates": {"lat": 35.6602, "lng": 139.7292},
                "opening_hours": {"open_now": True},
                "photos": ["mori.jpg"],
            },
        ]
    )
    enrichment = FakeVenueEnrichmentCollection(
        [
            {
                "category_pattern": "temple",
                "google_place_types": ["place_of_worship", "tourist_attraction"],
                "physical_intensity": "low",
                "estimated_duration_minutes": 60,
                "crowd_peak_weekday": {"start": "10:00", "end": "14:00"},
                "crowd_peak_weekend": {"start": "09:00", "end": "16:00"},
                "customs": {"shoes_off": True, "behavioural_notes": "bow at the gate"},
                "dietary_relevance": "none",
                "child_friendly": True,
                "elderly_friendly": True,
                "wheelchair_accessibility": "partial",
            },
            {
                "category_pattern": "museum",
                "google_place_types": ["museum", "art_gallery", "tourist_attraction"],
                "physical_intensity": "medium",
                "estimated_duration_minutes": 120,
                "crowd_peak_weekday": {"start": "11:00", "end": "15:00"},
                "crowd_peak_weekend": {"start": "10:00", "end": "17:00"},
                "customs": {"behavioural_notes": "no flash"},
                "dietary_relevance": "low",
                "child_friendly": True,
                "elderly_friendly": True,
                "wheelchair_accessibility": "full",
            },
        ]
    )

    result = search_venues(
        city="Tokyo",
        destination_country="Japan",
        date="2026-07-05",
        categories=["museum", "temple"],
        group_dietary_restrictions=[],
        group_interests=["art", "culture"],
        mobility_max="full",
        group_size=10,
        places_client=places,
        enrichment_collection=enrichment,
        limit=1,
    )

    assert result["total_found"] == 2
    assert [venue["name"] for venue in result["venues"]] == ["Mori Art Museum"]
    venue = result["venues"][0]
    assert venue["place_id"] == "place_mori"
    assert venue["category_pattern"] == "museum"
    assert venue["estimated_duration_minutes"] == 120
    assert venue["customs"] == {"behavioural_notes": "no flash"}
    assert places.calls == [
        {
            "city": "Tokyo",
            "destination_country": "Japan",
            "date": "2026-07-05",
            "place_types": ["museum", "place_of_worship", "tourist_attraction"],
            "limit": 20,
        }
    ]
    assert enrichment.queries == [{}]


def test_search_venues_filters_wheelchair_and_dietary_incompatible_food_venues():
    """Wheelchair groups and dietary needs should remove incompatible candidates."""
    places = FakePlacesClient(
        [
            {
                "place_id": "ramen_no_halal",
                "name": "Tiny Ramen Bar",
                "types": ["restaurant", "food"],
                "rating": 4.9,
                "coordinates": {"lat": 35.0, "lng": 139.0},
                "dietary_supported": ["vegetarian"],
            },
            {
                "place_id": "halal_sushi",
                "name": "Halal Sushi Tokyo",
                "types": ["restaurant", "food"],
                "rating": 4.4,
                "coordinates": {"lat": 35.1, "lng": 139.1},
                "dietary_supported": ["halal", "vegetarian"],
            },
            {
                "place_id": "stairs_market",
                "name": "Old Stairs Market",
                "types": ["market", "food"],
                "rating": 4.8,
                "coordinates": {"lat": 35.2, "lng": 139.2},
                "dietary_supported": ["halal"],
            },
        ]
    )
    enrichment = FakeVenueEnrichmentCollection(
        [
            {
                "category_pattern": "restaurant",
                "google_place_types": ["restaurant", "food"],
                "physical_intensity": "low",
                "estimated_duration_minutes": 90,
                "crowd_peak_weekday": {"start": "12:00", "end": "14:00"},
                "crowd_peak_weekend": {"start": "18:00", "end": "21:00"},
                "customs": {"behavioural_notes": "confirm allergies"},
                "dietary_relevance": "high",
                "child_friendly": True,
                "elderly_friendly": True,
                "wheelchair_accessibility": "full",
            },
            {
                "category_pattern": "market",
                "google_place_types": ["market", "food"],
                "physical_intensity": "medium",
                "estimated_duration_minutes": 90,
                "crowd_peak_weekday": {"start": "10:00", "end": "13:00"},
                "crowd_peak_weekend": {"start": "09:00", "end": "15:00"},
                "customs": {"behavioural_notes": "queue politely"},
                "dietary_relevance": "high",
                "child_friendly": True,
                "elderly_friendly": True,
                "wheelchair_accessibility": "partial",
            },
        ]
    )

    result = search_venues(
        city="Tokyo",
        destination_country="Japan",
        date="2026-07-05",
        categories=["restaurant", "market"],
        group_dietary_restrictions=["halal"],
        group_interests=["food"],
        mobility_max="wheelchair",
        group_size=10,
        places_client=places,
        enrichment_collection=enrichment,
    )

    assert result == {
        "venues": [
            {
                "place_id": "halal_sushi",
                "name": "Halal Sushi Tokyo",
                "types": ["restaurant", "food"],
                "rating": 4.4,
                "coordinates": {"lat": 35.1, "lng": 139.1},
                "opening_hours": None,
                "photos": [],
                "dietary_supported": ["halal", "vegetarian"],
                "category_pattern": "restaurant",
                "physical_intensity": "low",
                "estimated_duration_minutes": 90,
                "crowd_peak_weekday": {"start": "12:00", "end": "14:00"},
                "crowd_peak_weekend": {"start": "18:00", "end": "21:00"},
                "customs": {"behavioural_notes": "confirm allergies"},
                "dietary_relevance": "high",
                "child_friendly": True,
                "elderly_friendly": True,
                "wheelchair_accessibility": "full",
            }
        ],
        "total_found": 1,
    }


def test_search_venues_uses_safe_fallback_enrichment_when_no_pattern_matches():
    """Unknown place types should still return safe category fallback defaults."""
    places = FakePlacesClient(
        [
            {
                "place_id": "odd_place",
                "name": "Odd But Good",
                "types": ["aquarium"],
                "rating": 4.1,
                "coordinates": {"lat": 35.3, "lng": 139.3},
            }
        ]
    )
    enrichment = FakeVenueEnrichmentCollection([])

    result = search_venues(
        city="Tokyo",
        destination_country="Japan",
        date="2026-07-05",
        categories=[],
        group_dietary_restrictions=[],
        group_interests=[],
        mobility_max="full",
        group_size=2,
        places_client=places,
        enrichment_collection=enrichment,
    )

    assert result["total_found"] == 1
    assert result["venues"][0] == {
        "place_id": "odd_place",
        "name": "Odd But Good",
        "types": ["aquarium"],
        "rating": 4.1,
        "coordinates": {"lat": 35.3, "lng": 139.3},
        "opening_hours": None,
        "photos": [],
        "dietary_supported": [],
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
