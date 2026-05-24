from fastapi.testclient import TestClient
import sys

from api.email_client import reset_email_client
from api.main import app
from api.routes.disruptions import (
    get_contacts_collection_fn,
    get_db,
    get_firebase_broadcaster,
    get_now_fn,
    get_notify_contacts_fn,
    get_rank_alternatives_fn,
    get_search_venues_nearby_fn,
    get_transit_time_fn,
)


class FakeCollection:
    def __init__(self, records=None):
        self.records = records or []
        self.find_one_queries = []
        self.inserted = []
        self.find_queries = []

    def find_one(self, query):
        self.find_one_queries.append(query)
        for record in self.records:
            if all(record.get(key) == value for key, value in query.items()):
                return record
        return None

    def find(self, query):
        self.find_queries.append(query)
        return [record for record in self.records if all(record.get(k) == v for k, v in query.items())]

    def insert_one(self, document):
        self.inserted.append(document)
        self.records.append(document)
        return None


class FakeDB:
    def __init__(self):
        self.itineraries = FakeCollection(
            [
                {
                    "itinerary_id": "iti_tokyo",
                    "trip_id": "trip_tokyo",
                    "days": [
                        {
                            "day_number": 7,
                            "date": "2026-07-11",
                            "shared_schedule": [
                                {"venue_id": "teamlab", "arrival_time": "10:00", "departure_time": "12:00"},
                                {"venue_id": "dinner", "arrival_time": "18:00", "departure_time": "20:00"},
                            ],
                        }
                    ],
                }
            ]
        )
        self.group_trips = FakeCollection([{"trip_id": "trip_tokyo", "members": ["alex", "priya"]}])
        self.traveller_profiles = FakeCollection(
            [
                {"user_id": "alex", "dietary_restrictions": ["halal"], "mobility": "full"},
                {"user_id": "priya", "dietary_restrictions": ["vegetarian"], "mobility": "limited"},
            ]
        )
        self.disruption_events = FakeCollection([])
        self.contacts = FakeCollection(
            [{"trip_id": "trip_tokyo", "name": "Layla Hassan", "email": "layla.hassan@example.com", "detail_level": "updates_only", "language": "en"}]
        )
        self.notification_logs = FakeCollection([])


class FakeFirebaseBroadcaster:
    def __init__(self):
        self.broadcasts = []

    def broadcast_itinerary_update(self, trip_id, payload):
        self.broadcasts.append({"trip_id": trip_id, "payload": payload})


class FakeSendGridClient:
    """Echoes emails to stdout; returns a deterministic mock message_id."""

    def __init__(self, from_email: str = "bounce@yourdomain.com"):
        self._from_email = from_email
        self._sent = []

    def send_email(self, to_email: str, subject: str, body: str):
        msg_id = f"fake_msg_{len(self._sent) + 1}"
        self._sent.append({"to_email": to_email, "subject": subject, "body": body})
        print(f"[FakeSendGrid] 📧  TO: {to_email} | SUBJECT: {subject}", file=sys.stdout)
        return {"message_id": msg_id}

    @property
    def sent(self):
        return self._sent


def install_overrides(db=None, broadcaster=None, email_client=None):
    app.dependency_overrides.clear()
    reset_email_client()
    fake_db = db or FakeDB()
    fake_broadcaster = broadcaster or FakeFirebaseBroadcaster()
    fake_email = email_client or FakeSendGridClient()

    candidates = [
        {"venue_id": "mori", "name": "Mori Art Museum", "coordinates": {"lat": 35.66, "lng": 139.72}, "estimated_duration_minutes": 120},
        {"venue_id": "ueno", "name": "Ueno Park", "coordinates": {"lat": 35.71, "lng": 139.77}, "estimated_duration_minutes": 90},
    ]

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_search_venues_nearby_fn] = lambda: (lambda **kwargs: candidates)
    app.dependency_overrides[get_transit_time_fn] = lambda: (lambda *args, **kwargs: {"duration_minutes": 18, "mode": "transit"})
    app.dependency_overrides[get_rank_alternatives_fn] = lambda: (lambda reachable, profiles, available: reachable)
    app.dependency_overrides[get_firebase_broadcaster] = lambda: fake_broadcaster
    app.dependency_overrides[get_now_fn] = lambda: (lambda: "2026-07-11T09:30:00Z")
    app.dependency_overrides[get_contacts_collection_fn] = lambda: fake_db.contacts
    app.dependency_overrides[get_notify_contacts_fn] = lambda: _build_notify_contacts_fn(fake_email, fake_db)
    return fake_db, fake_broadcaster, fake_email


def _build_notify_contacts_fn(email_client, fake_db):
    """Build a notify_contacts fn bound to the given email client and DB collections."""
    from agent.tools.notify_contacts import notify_contacts

    def notify(trip_id, trigger_event, notification_context, notification_log_collection):
        return notify_contacts(
            trip_id=trip_id,
            trigger_event=trigger_event,
            notification_context=notification_context,
            contacts_collection=fake_db.contacts,
            notification_log_collection=notification_log_collection,
            send_email_fn=email_client.send_email,
            clock=lambda: "2026-07-11T09:30:00Z",
        )

    return notify


def teardown_function():
    app.dependency_overrides.clear()


def test_trigger_disruption_returns_alternatives_map_pins_and_broadcasts_firebase_update():
    db, broadcaster, email_client = install_overrides()
    client = TestClient(app)

    response = client.post(
        "/disruptions/trigger-disruption",
        json={
            "itinerary_id": "iti_tokyo",
            "event_type": "venue_closure",
            "description": "teamLab Borderless closed for a private event",
            "affected_day_numbers": [7],
            "current_location": {"lat": 35.6602, "lng": 139.7292},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["available_window_minutes"] == 480
    assert [alt["tier"] for alt in body["alternatives"]] == ["budget", "recommended"]
    assert body["map_pins"] == [
        {"venue_id": "mori", "name": "Mori Art Museum", "coordinates": {"lat": 35.66, "lng": 139.72}, "tier": "budget"},
        {"venue_id": "ueno", "name": "Ueno Park", "coordinates": {"lat": 35.71, "lng": 139.77}, "tier": "recommended"},
    ]
    assert db.disruption_events.inserted[0]["event_type"] == "venue_closure"
    assert broadcaster.broadcasts == [
        {
            "trip_id": "trip_tokyo",
            "payload": {
                "event_type": "venue_closure",
                "itinerary_id": "iti_tokyo",
                "last_disruption_at": "2026-07-11T09:30:00Z",
                "alternatives_count": 2,
            },
        }
    ]
    # Email notification assertions
    assert body["notification"]["sent"] == 1
    assert body["notification"]["failed"] == 0
    assert len(email_client.sent) == 1
    assert email_client.sent[0]["to_email"] == "layla.hassan@example.com"
    assert db.notification_logs.inserted[0]["status"] == "sent"


def test_trigger_disruption_returns_404_for_tool_error_without_broadcast():
    db = FakeDB()
    db.itineraries = FakeCollection([])
    broadcaster = FakeFirebaseBroadcaster()
    install_overrides(db, broadcaster)
    client = TestClient(app)

    response = client.post(
        "/disruptions/trigger-disruption",
        json={
            "itinerary_id": "missing",
            "event_type": "venue_closure",
            "description": "closed",
            "affected_day_numbers": [7],
            "current_location": {"lat": 35.6602, "lng": 139.7292},
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "ITINERARY_NOT_FOUND",
            "message": "Itinerary not found for itinerary_id 'missing'.",
        }
    }
    assert broadcaster.broadcasts == []
