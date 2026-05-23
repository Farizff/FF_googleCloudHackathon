from agent.tools.optimise_route import optimise_route


ACCOMMODATION = {"lat": 1.3000, "lng": 103.8000}


def venue(
    name,
    lat,
    lng,
    open_time,
    close_time="18:00",
    duration=60,
    types=None,
    dietary_supported=None,
    physical_intensity="medium",
    child_friendly=True,
    elderly_friendly=True,
    wheelchair_accessibility="full",
    peak=None,
    energy_cost=2.0,
):
    return {
        "place_id": name.lower().replace(" ", "_"),
        "name": name,
        "types": types or ["tourist_attraction"],
        "coordinates": {"lat": lat, "lng": lng},
        "opening_hours": {
            "monday": {"open": open_time, "close": close_time},
            "tuesday": {"open": open_time, "close": close_time},
        },
        "dietary_supported": dietary_supported or [],
        "physical_intensity": physical_intensity,
        "estimated_duration_minutes": duration,
        "child_friendly": child_friendly,
        "elderly_friendly": elderly_friendly,
        "wheelchair_accessibility": wheelchair_accessibility,
        "crowd_peak_weekday": peak or {"start": "11:00", "end": "13:00"},
        "crowd_peak_weekend": {"start": "10:00", "end": "16:00"},
        "energy_cost": energy_cost,
        "reasoning": "",
    }


def group_profile(**overrides):
    profile = {
        "size": 4,
        "members": [{"age": 34}, {"age": 32}],
        "dietary_restrictions": [],
        "mobility_max": "full",
        "arrival_date": "2026-07-05",
    }
    profile.update(overrides)
    return profile


def test_optimise_route_filters_then_orders_by_geographic_cluster_and_opening_time():
    """Eligible venues should be clustered near accommodation, then ordered by cluster and opening time."""
    venues = [
        venue("Closed Museum", 1.3005, 103.8005, None, close_time=None),
        venue("Far Later Gallery", 1.3400, 103.8400, "09:30"),
        venue("Near Later Park", 1.3004, 103.8004, "10:00"),
        venue("Near Early Temple", 1.3002, 103.8002, "08:30"),
        venue("Far Early Tower", 1.3403, 103.8403, "09:00"),
        venue(
            "Incompatible Ramen",
            1.3006,
            103.8006,
            "08:00",
            types=["restaurant", "food"],
            dietary_supported=["vegetarian"],
        ),
        venue("Mobility Heavy Hike", 1.3007, 103.8007, "08:15", wheelchair_accessibility="none"),
    ]

    result = optimise_route(
        venues=venues,
        date="2026-07-06",
        start_time="08:00",
        pace="moderate",
        group_profile=group_profile(dietary_restrictions=["halal"], mobility_max="wheelchair"),
        accommodation_coords=ACCOMMODATION,
        transit_fn=lambda **_: {"duration_minutes": 0, "mode": "walking"},
    )

    assert [item["name"] for item in result] == [
        "Near Early Temple",
        "Near Later Park",
        "Far Early Tower",
        "Far Later Gallery",
    ]


def test_optimise_route_assigns_arrival_departure_and_uses_injected_transit_between_venues():
    """Timing should wait for opening, add visit duration, and call only the injected transit function."""
    calls = []

    def transit_fn(**kwargs):
        calls.append(kwargs)
        return {"duration_minutes": 20, "mode": "transit", "group_transport_note": "use MRT together"}

    venues = [
        venue("First Stop", 1.3001, 103.8001, "09:00", duration=45),
        venue("Second Stop", 1.3002, 103.8002, "10:00", duration=30),
    ]

    result = optimise_route(
        venues=venues,
        date="2026-07-06",
        start_time="08:30",
        pace="moderate",
        group_profile=group_profile(size=8),
        accommodation_coords=ACCOMMODATION,
        transit_fn=transit_fn,
    )

    assert result[0]["arrival_time"] == "09:00"
    assert result[0]["departure_time"] == "09:45"
    assert result[0]["transit_to_next_minutes"] == 20
    assert result[0]["transit_mode"] == "transit"
    assert result[0]["group_transport_note"] == "use MRT together"
    assert result[1]["arrival_time"] == "10:05"
    assert result[1]["departure_time"] == "10:35"
    assert calls == [
        {
            "origin": {"lat": 1.3001, "lng": 103.8001},
            "destination": {"lat": 1.3002, "lng": 103.8002},
            "departure_time": "09:45",
            "group_size": 8,
        }
    ]


def test_optimise_route_annotates_peak_hour_overlap_in_reasoning():
    """A visit overlapping venue crowd peaks should receive a deterministic warning."""
    result = optimise_route(
        venues=[venue("Popular Market", 1.3001, 103.8001, "09:00", duration=90, peak={"start": "09:30", "end": "11:00"})],
        date="2026-07-06",
        start_time="09:00",
        pace="moderate",
        group_profile=group_profile(),
        accommodation_coords=ACCOMMODATION,
        transit_fn=lambda **_: {"duration_minutes": 0, "mode": "walking"},
    )

    assert "arrives during peak hours (09:30–11:00)" in result[0]["reasoning"]
    assert "Consider shifting earlier" in result[0]["reasoning"]


def test_optimise_route_inserts_child_rest_and_early_breather_when_energy_budget_is_stressed():
    """Children and jet lag should reduce energy budget, causing a midday rest and early breather."""
    venues = [
        venue("Morning Zoo", 1.3001, 103.8001, "09:00", duration=60, energy_cost=5.0),
        venue("Science Centre", 1.3002, 103.8002, "10:00", duration=60, energy_cost=5.0),
        venue("Botanic Walk", 1.3003, 103.8003, "11:00", duration=60, energy_cost=2.0),
    ]

    result = optimise_route(
        venues=venues,
        date="2026-07-06",
        start_time="09:00",
        pace="relaxed",
        group_profile=group_profile(
            members=[{"age": 38}, {"age": 7}],
            jet_lag_active=True,
            arrival_date="2026-07-05",
        ),
        accommodation_coords=ACCOMMODATION,
        transit_fn=lambda **_: {"duration_minutes": 0, "mode": "walking"},
    )

    block_types = [item.get("type") for item in result]
    assert "breather" in block_types
    assert "rest" in block_types
    breather = next(item for item in result if item.get("type") == "breather")
    rest = next(item for item in result if item.get("type") == "rest")
    assert breather["duration_minutes"] == 30
    assert "covered a lot of ground" in breather["reasoning"]
    assert rest["arrival_time"] == "13:00"
    assert rest["departure_time"] == "14:00"


def test_optimise_route_returns_standard_error_when_no_venues_are_eligible():
    """If filters remove every venue, the tool should fail loud with a standard error shape."""
    result = optimise_route(
        venues=[venue("Closed Place", 1.3001, 103.8001, None, close_time=None)],
        date="2026-07-06",
        start_time="09:00",
        pace="moderate",
        group_profile=group_profile(),
        accommodation_coords=ACCOMMODATION,
        transit_fn=lambda **_: {"duration_minutes": 0, "mode": "walking"},
    )

    assert result == {
        "error": {
            "code": "NO_ELIGIBLE_VENUES",
            "message": "No eligible venues remain after route filters for 2026-07-06.",
        }
    }
