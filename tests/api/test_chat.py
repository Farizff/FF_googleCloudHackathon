"""Tests for real trip creation via POST /chat endpoint."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from api.main import app
from api.routes import chat
from api.routes import trip as trip_module


class FakePublisher:
    def __init__(self):
        self.messages = []

    def publish_main_thread_message(self, *, trip_id, author_id, text, role, message_id):
        self.messages.append(
            {
                "trip_id": trip_id,
                "author_id": author_id,
                "text": text,
                "role": role,
                "message_id": message_id,
            }
        )
        return f"/trips/{trip_id}/threads/main/{message_id}"


def install_overrides(publisher=None, now=1000.0):
    app.dependency_overrides.clear()
    chat.rate_buckets.clear()
    fake_publisher = publisher or FakePublisher()
    app.dependency_overrides[chat.get_chat_publisher] = lambda: fake_publisher
    app.dependency_overrides[chat.get_time_fn] = lambda: (lambda: now)
    return fake_publisher


def teardown_function():
    app.dependency_overrides.clear()
    chat.rate_buckets.clear()
    # Restore original get_db if we patched it
    if hasattr(trip_module, '_original_get_db'):
        trip_module.get_db = trip_module._original_get_db


def _make_mock_db():
    """Create a mock DB that captures inserted documents."""
    mock_db = MagicMock()
    inserted = []

    def capture_insert(doc):
        inserted.append(doc)
        return MagicMock(inserted_id="mock_id")

    mock_db.group_trips.insert_one = capture_insert
    return mock_db, inserted


def test_chat_creates_real_trip_when_no_trip_id_provided():
    """POST /chat without trip_id should create a real trip document in MongoDB."""
    mock_db, inserted = _make_mock_db()

    # Patch module-level get_db directly (used by create_trip_from_extraction)
    trip_module._original_get_db = trip_module.get_db
    trip_module.get_db = lambda: mock_db

    try:
        fake_publisher = install_overrides()
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={
                "user_id": "u_test_user",
                "message": "Plan a 5 day Barcelona trip for 4 friends in September.",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["trip_id"].startswith("trip_")
        assert body["intent"] == "full_trip_planning"

        # Verify a real document was inserted into MongoDB
        assert len(inserted) == 1
        doc = inserted[0]
        assert doc["trip_id"] == body["trip_id"]
        assert doc["destination_city"] == "Barcelona"
        assert doc["destination_country"] == "Spain"
        assert doc["destination_iata"] == "BCN"
        assert doc["status"] == "planning"
        assert doc["group_type"] == "friends"
        assert doc["trip_mode"] == "international"
        # Check member was added as organiser
        assert len(doc["members"]) == 1
        assert doc["members"][0]["user_id"] == "u_test_user"
        assert doc["members"][0]["role"] == "organiser"

        # Publisher should have been called with the new trip_id
        assert len(fake_publisher.messages) == 1
        assert fake_publisher.messages[0]["trip_id"] == body["trip_id"]
    finally:
        trip_module.get_db = trip_module._original_get_db


def test_chat_reuses_trip_id_when_provided():
    """When trip_id is already provided, chat should NOT create a new trip."""
    mock_db, inserted = _make_mock_db()
    trip_module._original_get_db = trip_module.get_db
    trip_module.get_db = lambda: mock_db

    try:
        fake_publisher = install_overrides()
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={
                "user_id": "u_alex",
                "message": "Add a museum to the itinerary.",
                "trip_id": "trip_tokyo_reunion_2026",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["trip_id"] == "trip_tokyo_reunion_2026"
        # Should NOT have created a new trip
        assert len(inserted) == 0
    finally:
        trip_module.get_db = trip_module._original_get_db


def test_chat_extracts_destination_and_date_from_natural_message():
    """Chat should extract destination city, departure date from natural language."""
    mock_db, inserted = _make_mock_db()
    trip_module._original_get_db = trip_module.get_db
    trip_module.get_db = lambda: mock_db

    try:
        fake_publisher = install_overrides()
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={
                "user_id": "u_jane",
                "message": "I want to plan a 7 night honeymoon in Bali in December.",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True

        assert len(inserted) == 1
        doc = inserted[0]
        assert doc["destination_city"] == "Bali"
        assert doc["destination_country"] == "Indonesia"
        assert doc["destination_iata"] == "DPS"
        assert doc["special_occasion"] == "honeymoon"
        assert doc["departure_date"] is not None
        assert "12" in doc["departure_date"]
    finally:
        trip_module.get_db = trip_module._original_get_db


def test_chat_returns_trip_id_in_response():
    """Chat response should include the newly created trip_id."""
    mock_db, inserted = _make_mock_db()
    trip_module._original_get_db = trip_module.get_db
    trip_module.get_db = lambda: mock_db

    try:
        fake_publisher = install_overrides()
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={
                "user_id": "u_new_user",
                "message": "Plan a weekend trip to Paris.",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert "trip_id" in body
        assert body["trip_id"].startswith("trip_")
        assert body["intent"] == "full_trip_planning"
        assert len(body["loading_states"]) == 4
        assert len(body["actions"]) == 3  # extract_trip_fields, create_trip, start_planning_response
    finally:
        trip_module.get_db = trip_module._original_get_db