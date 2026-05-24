from agent.tools.search_accommodation import search_accommodation


class FakeHotelPlacesClient:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def hotel_search(self, **kwargs):
        self.calls.append(kwargs)
        return list(self.results)


class FakePriceEstimator:
    def __init__(self):
        self.calls = []

    def estimate_price_per_night_usd(self, **kwargs):
        self.calls.append(kwargs)
        category = kwargs["category"]
        return {"budget": 92, "mid_range": 184, "premium": 365}[category]


def test_search_accommodation_returns_three_labelled_options_with_disclaimer():
    places = FakeHotelPlacesClient(
        [
            {
                "place_id": "hotel_capsule",
                "name": "Tokyo Capsule Stay",
                "address": "1 Budget Lane, Tokyo",
                "coordinates": {"lat": 35.67, "lng": 139.76},
                "rating": 4.0,
                "types": ["lodging"],
                "category": "budget",
                "booking_url": "https://booking.com/tokyo-capsule",
            },
            {
                "place_id": "hotel_mid",
                "name": "Shinjuku Central Hotel",
                "address": "2 Central Ave, Tokyo",
                "coordinates": {"lat": 35.69, "lng": 139.70},
                "rating": 4.5,
                "types": ["lodging"],
                "category": "mid_range",
                "booking_url": "https://hotels.com/shinjuku-central",
            },
            {
                "place_id": "hotel_luxe",
                "name": "Ginza Sky Hotel",
                "address": "3 Premium Road, Tokyo",
                "coordinates": {"lat": 35.66, "lng": 139.76},
                "rating": 4.8,
                "types": ["lodging"],
                "category": "premium",
                "booking_url": "https://agoda.com/ginza-sky",
            },
        ]
    )
    estimator = FakePriceEstimator()

    result = search_accommodation(
        city="Tokyo",
        check_in="2026-10-15",
        check_out="2026-10-25",
        group_size=10,
        budget_tier="recommended",
        places_client=places,
        price_estimator=estimator,
    )

    assert places.calls == [
        {
            "city": "Tokyo",
            "check_in": "2026-10-15",
            "check_out": "2026-10-25",
            "group_size": 10,
            "place_types": ["lodging"],
            "limit": 20,
        }
    ]
    assert [option["tier"] for option in result["options"]] == ["budget", "recommended", "premium"]
    assert [option["name"] for option in result["options"]] == [
        "Tokyo Capsule Stay",
        "Shinjuku Central Hotel",
        "Ginza Sky Hotel",
    ]
    assert [option["price_per_night_usd"] for option in result["options"]] == [92, 184, 365]
    assert all(option["price_note"] == "Final price confirmed at booking site." for option in result["options"])
    assert estimator.calls == [
        {"city": "Tokyo", "category": "budget", "group_size": 10, "check_in": "2026-10-15", "check_out": "2026-10-25"},
        {"city": "Tokyo", "category": "mid_range", "group_size": 10, "check_in": "2026-10-15", "check_out": "2026-10-25"},
        {"city": "Tokyo", "category": "premium", "group_size": 10, "check_in": "2026-10-15", "check_out": "2026-10-25"},
    ]


def test_search_accommodation_categorizes_unlabelled_hotels_by_rating_and_price():
    places = FakeHotelPlacesClient(
        [
            {"place_id": "a", "name": "Five Star", "rating": 4.9, "price_level": 4},
            {"place_id": "b", "name": "Simple Inn", "rating": 3.8, "price_level": 1},
            {"place_id": "c", "name": "Solid Hotel", "rating": 4.4, "price_level": 2},
            {"place_id": "d", "name": "Another Mid", "rating": 4.2, "price_level": 2},
        ]
    )

    result = search_accommodation("Tokyo", "2026-10-15", "2026-10-25", 4, "budget", places)

    assert [option["tier"] for option in result["options"]] == ["budget", "recommended", "premium"]
    assert [option["name"] for option in result["options"]] == ["Simple Inn", "Solid Hotel", "Five Star"]
    assert [option["category"] for option in result["options"]] == ["budget", "mid_range", "premium"]


def test_search_accommodation_returns_available_options_when_fewer_than_three_exist():
    places = FakeHotelPlacesClient(
        [
            {"place_id": "only", "name": "Only Good Hotel", "rating": 4.2, "price_level": 2},
        ]
    )

    result = search_accommodation("Kyoto", "2026-10-15", "2026-10-20", 2, "recommended", places)

    assert result["options"] == [
        {
            "tier": "recommended",
            "place_id": "only",
            "name": "Only Good Hotel",
            "address": None,
            "coordinates": None,
            "rating": 4.2,
            "types": [],
            "category": "mid_range",
            "price_per_night_usd": 180,
            "price_note": "Final price confirmed at booking site.",
            "booking_url": None,
        }
    ]
    assert result["note"] == "Only 1 accommodation option was available."


def test_search_accommodation_filters_unapproved_booking_domains():
    places = FakeHotelPlacesClient(
        [
            {
                "place_id": "bad_link",
                "name": "Suspicious Hotel",
                "rating": 4.8,
                "price_level": 3,
                "booking_url": "https://evil.example/pay-now",
            },
            {
                "place_id": "good_link",
                "name": "Safe Hotel",
                "rating": 4.4,
                "price_level": 2,
                "booking_url": "https://www.booking.com/safe-hotel",
            },
        ]
    )

    result = search_accommodation("Tokyo", "2026-10-15", "2026-10-20", 2, "recommended", places)

    urls = {option["name"]: option["booking_url"] for option in result["options"]}
    assert urls["Suspicious Hotel"] is None
    assert urls["Safe Hotel"] == "https://www.booking.com/safe-hotel"
