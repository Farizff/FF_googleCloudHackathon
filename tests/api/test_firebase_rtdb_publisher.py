import pytest
from fastapi.testclient import TestClient

from api.firebase_rtdb import FirebaseProviderNotConfigured, FirebaseRtdbPublisher
from api.main import app
from api.routes import chat


class FakeRequester:
    def __init__(self):
        self.calls = []

    def __call__(self, method, url, payload):
        self.calls.append({"method": method, "url": url, "payload": payload})
        return {"ok": True}


def teardown_function():
    app.dependency_overrides.clear()
    chat.rate_buckets.clear()


def test_rtdb_publisher_writes_chat_message_to_prd_main_thread_path():
    requester = FakeRequester()
    publisher = FirebaseRtdbPublisher(
        database_url="https://bounce-demo.asia-southeast1.firebasedatabase.app",
        request_json=requester,
    )

    path = publisher.publish_main_thread_message(
        trip_id="trip_tokyo",
        author_id="bounce",
        text="Planning response ready.",
        role="assistant",
        message_id="msg_123",
    )

    assert path == "/trips/trip_tokyo/threads/main/msg_123"
    assert requester.calls == [
        {
            "method": "PUT",
            "url": "https://bounce-demo.asia-southeast1.firebasedatabase.app/trips/trip_tokyo/threads/main/msg_123.json",
            "payload": {
                "message_id": "msg_123",
                "author_id": "bounce",
                "role": "assistant",
                "text": "Planning response ready.",
            },
        }
    ]


def test_rtdb_publisher_broadcasts_itinerary_and_group_state_updates():
    requester = FakeRequester()
    publisher = FirebaseRtdbPublisher(
        database_url="https://bounce-demo.asia-southeast1.firebasedatabase.app/",
        request_json=requester,
    )

    publisher.broadcast_itinerary_update(
        "trip_tokyo",
        {"itinerary_id": "iti_1", "last_disruption_at": "2026-07-11T09:30:00Z"},
    )
    publisher.broadcast_group_state("trip_tokyo", {"members_ready": 7})

    assert requester.calls == [
        {
            "method": "PATCH",
            "url": "https://bounce-demo.asia-southeast1.firebasedatabase.app/trips/trip_tokyo/state/itinerary.json",
            "payload": {"itinerary_id": "iti_1", "last_disruption_at": "2026-07-11T09:30:00Z"},
        },
        {
            "method": "PATCH",
            "url": "https://bounce-demo.asia-southeast1.firebasedatabase.app/trips/trip_tokyo/state/group.json",
            "payload": {"members_ready": 7},
        },
    ]


def test_rtdb_publisher_fails_loudly_when_database_url_missing():
    with pytest.raises(FirebaseProviderNotConfigured, match="FIREBASE_DATABASE_URL"):
        FirebaseRtdbPublisher(database_url="", request_json=FakeRequester())


def test_chat_route_maps_firebase_provider_failure_to_503():
    class FailingPublisher:
        def publish_main_thread_message(self, **kwargs):
            raise FirebaseProviderNotConfigured("FIREBASE_DATABASE_URL is not configured.")

    app.dependency_overrides[chat.get_chat_publisher] = lambda: FailingPublisher()
    app.dependency_overrides[chat.get_time_fn] = lambda: (lambda: 1234.0)
    client = TestClient(app)

    response = client.post("/chat", json={"user_id": "u_alex", "message": "Plan Tokyo", "trip_id": "trip_tokyo"})

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "FIREBASE_PROVIDER_NOT_CONFIGURED",
            "message": "Firebase Realtime Database is not configured.",
        }
    }
