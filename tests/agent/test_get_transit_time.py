from agent.tools.get_transit_time import get_transit_time


class FakeDirectionsClient:
    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def get_directions(self, **kwargs):
        self.calls.append(kwargs)
        return self.routes


def test_get_transit_time_returns_duration_distance_and_calls_injected_client():
    """Transit time should come from the injected directions client, not live Google Maps."""
    directions = FakeDirectionsClient(
        [
            {
                "legs": [
                    {
                        "duration": {"value": 1_500},
                        "distance": {"value": 12_340},
                    }
                ]
            }
        ]
    )

    result = get_transit_time(
        origin={"lat": 1.3521, "lng": 103.8198},
        destination={"lat": 1.2834, "lng": 103.8607},
        departure_unix_timestamp=1_781_234_567,
        mode="transit",
        group_size=4,
        directions_client=directions,
    )

    assert result == {
        "duration_minutes": 25,
        "distance_km": 12.34,
        "mode": "transit",
        "group_transport_note": None,
    }
    assert directions.calls == [
        {
            "origin": {"lat": 1.3521, "lng": 103.8198},
            "destination": {"lat": 1.2834, "lng": 103.8607},
            "departure_time": 1_781_234_567,
            "mode": "transit",
        }
    ]


def test_get_transit_time_prefers_traffic_duration_when_available_for_driving():
    """Driving estimates should use duration_in_traffic when the directions result provides it."""
    directions = FakeDirectionsClient(
        [
            {
                "legs": [
                    {
                        "duration": {"value": 1_200},
                        "duration_in_traffic": {"value": 1_800},
                        "distance": {"value": 5_000},
                    }
                ]
            }
        ]
    )

    result = get_transit_time(
        origin={"lat": 35.6812, "lng": 139.7671},
        destination={"lat": 35.6586, "lng": 139.7454},
        departure_unix_timestamp=1_781_234_567,
        mode="driving",
        group_size=2,
        directions_client=directions,
    )

    assert result["duration_minutes"] == 30
    assert result["distance_km"] == 5.0
    assert result["mode"] == "driving"


def test_get_transit_time_adds_group_transport_note_for_large_groups():
    """Groups larger than six should receive deterministic transport planning guidance."""
    directions = FakeDirectionsClient(
        [
            {
                "legs": [
                    {
                        "duration": {"value": 900},
                        "distance": {"value": 4_200},
                    }
                ]
            }
        ]
    )

    result = get_transit_time(
        origin={"lat": 1.3521, "lng": 103.8198},
        destination={"lat": 1.2834, "lng": 103.8607},
        departure_unix_timestamp=1_781_234_567,
        mode="driving",
        group_size=10,
        directions_client=directions,
    )

    assert result == {
        "duration_minutes": 15,
        "distance_km": 4.2,
        "mode": "driving",
        "group_transport_note": "10 people: chartered minibus (~$80) or 3 taxis (~$95 total).",
    }
