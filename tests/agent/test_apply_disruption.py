from agent.tools.apply_disruption import apply_disruption


class FakeCollection:
    def __init__(self, records=None):
        self.records = records or []
        self.find_one_queries = []
        self.inserted = []

    def find_one(self, query):
        self.find_one_queries.append(query)
        for record in self.records:
            if all(record.get(key) == value for key, value in query.items()):
                return record
        return None

    def insert_one(self, document):
        self.inserted.append(document)
        return None


class FakeDB:
    def __init__(self, itinerary=None, trip=None, profiles=None):
        self.itineraries = FakeCollection([itinerary] if itinerary else [])
        self.group_trips = FakeCollection([trip] if trip else [])
        self.traveller_profiles = FakeCollection(profiles or [])
        self.disruption_events = FakeCollection([])


def base_itinerary():
    return {
        "itinerary_id": "iti_tokyo",
        "trip_id": "trip_tokyo",
        "days": [
            {
                "day_number": 7,
                "date": "2026-07-11",
                "shared_schedule": [
                    {
                        "venue_id": "teamlab_borderless",
                        "name": "teamLab Borderless",
                        "arrival_time": "10:00",
                        "departure_time": "12:00",
                    },
                    {
                        "venue_id": "dinner_shibuya",
                        "name": "Dinner in Shibuya",
                        "arrival_time": "18:00",
                        "departure_time": "20:00",
                    },
                ],
            }
        ],
    }


def base_trip():
    return {"trip_id": "trip_tokyo", "members": ["alex", "priya", "emma"]}


def base_profiles():
    return [
        {"user_id": "alex", "dietary_restrictions": ["halal"], "mobility": "full"},
        {"user_id": "priya", "dietary_restrictions": ["vegetarian"], "mobility": "limited"},
        {"user_id": "emma", "dietary_restrictions": [], "mobility": "full"},
    ]


def test_apply_disruption_logs_event_calculates_window_and_returns_notification_context():
    db = FakeDB(base_itinerary(), base_trip(), base_profiles())

    def search(**kwargs):
        return []

    result = apply_disruption(
        itinerary_id="iti_tokyo",
        event_type="venue_closure",
        affected_day_numbers=[7],
        current_location={"lat": 35.6602, "lng": 139.7292},
        description="teamLab Borderless closed for a private event",
        db=db,
        search_venues_nearby_fn=search,
        get_transit_time_fn=lambda *args, **kwargs: {"duration_minutes": 0, "mode": "transit"},
        rank_alternatives_fn=lambda candidates, profiles, available: candidates,
        now_fn=lambda: "2026-07-11T09:30:00Z",
    )

    assert db.disruption_events.inserted == [
        {
            "itinerary_id": "iti_tokyo",
            "event_type": "venue_closure",
            "description": "teamLab Borderless closed for a private event",
            "created_at": "2026-07-11T09:30:00Z",
        }
    ]
    assert result["available_window_minutes"] == 480
    assert result["notification_context"] == {
        "event_description": "teamLab Borderless closed for a private event",
        "changes_summary": "Day rebuilt with alternatives near current location.",
    }


def test_apply_disruption_aggregates_group_constraints_and_excludes_scheduled_venues():
    db = FakeDB(base_itinerary(), base_trip(), base_profiles())
    search_calls = []

    def search(**kwargs):
        search_calls.append(kwargs)
        return []

    apply_disruption(
        itinerary_id="iti_tokyo",
        event_type="venue_closure",
        affected_day_numbers=[7],
        current_location={"lat": 35.6602, "lng": 139.7292},
        description="closed",
        db=db,
        search_venues_nearby_fn=search,
        get_transit_time_fn=lambda *args, **kwargs: {"duration_minutes": 0, "mode": "transit"},
        rank_alternatives_fn=lambda candidates, profiles, available: candidates,
        now_fn=lambda: "2026-07-11T09:30:00Z",
    )

    assert search_calls == [
        {
            "coordinates": {"lat": 35.6602, "lng": 139.7292},
            "radius_km": 3,
            "date": "2026-07-11",
            "dietary_restrictions": ["halal", "vegetarian"],
            "mobility_max": "limited",
            "group_size": 3,
            "exclude_venue_ids": ["teamlab_borderless", "dinner_shibuya"],
            "limit": 15,
        }
    ]


def test_apply_disruption_filters_unreachable_candidates_before_ranking():
    db = FakeDB(base_itinerary(), base_trip(), base_profiles())
    candidates = [
        {"venue_id": "mori_art", "name": "Mori Art Museum", "coordinates": {"lat": 1}, "estimated_duration_minutes": 120},
        {"venue_id": "far_theme_park", "name": "Far Theme Park", "coordinates": {"lat": 2}, "estimated_duration_minutes": 420},
    ]
    ranked_inputs = []

    def transit(origin, destination, departure_unix_timestamp, group_size):
        del origin, departure_unix_timestamp, group_size
        if destination == {"lat": 1}:
            return {"duration_minutes": 18, "mode": "transit", "group_transport_note": "3 taxis may be easier."}
        return {"duration_minutes": 90, "mode": "transit"}

    def rank(reachable, profiles, available):
        ranked_inputs.append((reachable, profiles, available))
        return reachable

    result = apply_disruption(
        itinerary_id="iti_tokyo",
        event_type="venue_closure",
        affected_day_numbers=[7],
        current_location={"lat": 35.6602, "lng": 139.7292},
        description="closed",
        db=db,
        search_venues_nearby_fn=lambda **kwargs: candidates,
        get_transit_time_fn=transit,
        rank_alternatives_fn=rank,
        now_fn=lambda: "2026-07-11T09:30:00Z",
    )

    assert ranked_inputs[0][2] == 480
    assert ranked_inputs[0][0] == [
        {
            "venue_id": "mori_art",
            "name": "Mori Art Museum",
            "coordinates": {"lat": 1},
            "estimated_duration_minutes": 120,
            "transit_minutes_from_disruption": 18,
            "transit_mode_from_disruption": "transit",
            "group_transport_note": "3 taxis may be easier.",
        }
    ]
    assert result["alternatives"][0]["venue_id"] == "mori_art"


def test_apply_disruption_labels_up_to_three_ranked_alternatives():
    db = FakeDB(base_itinerary(), base_trip(), base_profiles())
    candidates = [
        {"venue_id": "free_park", "name": "Ueno Park", "coordinates": {"lat": 1}, "estimated_duration_minutes": 90},
        {"venue_id": "mori_art", "name": "Mori Art Museum", "coordinates": {"lat": 2}, "estimated_duration_minutes": 120},
        {"venue_id": "planets", "name": "teamLab Planets", "coordinates": {"lat": 3}, "estimated_duration_minutes": 120},
        {"venue_id": "extra", "name": "Extra Venue", "coordinates": {"lat": 4}, "estimated_duration_minutes": 60},
    ]

    result = apply_disruption(
        itinerary_id="iti_tokyo",
        event_type="venue_closure",
        affected_day_numbers=[7],
        current_location={"lat": 35.6602, "lng": 139.7292},
        description="closed",
        db=db,
        search_venues_nearby_fn=lambda **kwargs: candidates,
        get_transit_time_fn=lambda *args, **kwargs: {"duration_minutes": 5, "mode": "walk"},
        rank_alternatives_fn=lambda reachable, profiles, available: list(reversed(reachable)),
        now_fn=lambda: "2026-07-11T09:30:00Z",
    )

    assert [alt["tier"] for alt in result["alternatives"]] == ["budget", "recommended", "premium"]
    assert [alt["venue_id"] for alt in result["alternatives"]] == ["extra", "planets", "mori_art"]


def test_apply_disruption_returns_standard_error_when_itinerary_or_day_is_missing():
    db = FakeDB(itinerary=None, trip=base_trip(), profiles=base_profiles())

    missing_itinerary = apply_disruption(
        itinerary_id="missing",
        event_type="venue_closure",
        affected_day_numbers=[7],
        current_location={"lat": 35.6602, "lng": 139.7292},
        description="closed",
        db=db,
        search_venues_nearby_fn=lambda **kwargs: [],
        get_transit_time_fn=lambda *args, **kwargs: {"duration_minutes": 0, "mode": "transit"},
        rank_alternatives_fn=lambda candidates, profiles, available: candidates,
        now_fn=lambda: "2026-07-11T09:30:00Z",
    )

    assert missing_itinerary == {
        "error": {
            "code": "ITINERARY_NOT_FOUND",
            "message": "Itinerary not found for itinerary_id 'missing'.",
        }
    }

    db = FakeDB(base_itinerary(), base_trip(), base_profiles())
    missing_day = apply_disruption(
        itinerary_id="iti_tokyo",
        event_type="venue_closure",
        affected_day_numbers=[8],
        current_location={"lat": 35.6602, "lng": 139.7292},
        description="closed",
        db=db,
        search_venues_nearby_fn=lambda **kwargs: [],
        get_transit_time_fn=lambda *args, **kwargs: {"duration_minutes": 0, "mode": "transit"},
        rank_alternatives_fn=lambda candidates, profiles, available: candidates,
        now_fn=lambda: "2026-07-11T09:30:00Z",
    )

    assert missing_day == {
        "error": {
            "code": "AFFECTED_DAY_NOT_FOUND",
            "message": "No affected day found for day numbers [8] in itinerary 'iti_tokyo'.",
        }
    }
