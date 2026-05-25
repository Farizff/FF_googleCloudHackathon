from fastapi.testclient import TestClient
from pymongo.errors import ServerSelectionTimeoutError

from api.main import app
from api.routes.judge import get_db, get_now_fn
from db.client import MongoDBConfigError


class FakeCollection:
    def __init__(self, records=None):
        self.records = records or []
        self.deleted = []
        self.inserted = []
        self.replaced = []

    def delete_many(self, query):
        self.deleted.append(query)
        self.records = [record for record in self.records if not _matches(record, query)]
        return None

    def insert_one(self, document):
        self.inserted.append(document)
        self.records.append(document)
        return None

    def replace_one(self, query, document, upsert=False):
        self.replaced.append({"query": query, "document": document, "upsert": upsert})
        self.records = [record for record in self.records if not _matches(record, query)]
        if upsert:
            self.records.append(document)
        return None

    def find_one(self, query):
        for record in self.records:
            if _matches(record, query):
                return record
        return None


def _matches(record, query):
    for key, expected in query.items():
        actual = record.get(key)
        if isinstance(expected, dict) and "$in" in expected:
            if actual not in expected["$in"]:
                return False
        elif actual != expected:
            return False
    return True


class FakeDB:
    def __init__(self):
        self.group_trips = FakeCollection([])
        self.traveller_profiles = FakeCollection([])
        self.compliance_reminders = FakeCollection([])
        self.flocks = FakeCollection([])
        self.disruption_events = FakeCollection([])


def install_overrides(db=None):
    app.dependency_overrides.clear()
    fake_db = db or FakeDB()
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_now_fn] = lambda: (lambda: "2026-07-04T09:00:00Z")
    return fake_db


def teardown_function():
    app.dependency_overrides.clear()


def test_judge_seed_demo_trip_loads_reunion_seed_into_demo_collections():
    db = install_overrides()
    client = TestClient(app)

    response = client.post("/judge/seed-demo-trip")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "success": True,
        "trip_id": "trip_tokyo_reunion_2026",
        "trip_name": "The Tokyo Reunion",
        "invite_token": "invite_tokyo_reunion_demo",
        "members_seeded": 10,
        "profiles_seeded": 10,
        "compliance_reminders_seeded": 3,
        "flocks_seeded": 3,
    }
    assert db.group_trips.replaced[0]["query"] == {"trip_id": "trip_tokyo_reunion_2026"}
    assert db.group_trips.replaced[0]["upsert"] is True
    assert len(db.traveller_profiles.replaced) == 10
    assert len(db.compliance_reminders.replaced) == 3
    assert len(db.flocks.replaced) == 3


def test_judge_reset_clears_existing_demo_state_then_reseeds():
    db = install_overrides()
    client = TestClient(app)

    response = client.post("/judge/reset")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["reset"] is True
    assert body["seeded"]["trip_id"] == "trip_tokyo_reunion_2026"
    assert db.group_trips.deleted == [{"trip_id": "trip_tokyo_reunion_2026"}]
    assert db.traveller_profiles.deleted == [{"user_id": {"$in": ["u_alex", "u_priya", "u_marcus", "u_sofia", "u_jake", "u_aditya", "u_emma", "u_carlos", "u_liam", "u_rania"]}}]
    assert db.disruption_events.deleted == [{"itinerary_id": "iti_tokyo_reunion_2026"}]
    assert len(db.group_trips.replaced) == 1


def test_judge_trigger_disruption_records_demo_flight_cancellation():
    db = install_overrides()
    client = TestClient(app)

    response = client.post("/judge/trigger-disruption")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "event_type": "flight_cancellation",
        "itinerary_id": "iti_tokyo_reunion_2026",
        "affected_day_numbers": [3],
        "description": "Day 3 flight UA837 cancelled — judge demo disruption.",
    }
    assert db.disruption_events.inserted == [
        {
            "itinerary_id": "iti_tokyo_reunion_2026",
            "event_type": "flight_cancellation",
            "description": "Day 3 flight UA837 cancelled — judge demo disruption.",
            "affected_day_numbers": [3],
            "created_at": "2026-07-04T09:00:00Z",
            "judge_demo": True,
        }
    ]


def test_judge_seed_returns_503_when_mongodb_provider_is_not_configured(monkeypatch):
    app.dependency_overrides.clear()

    def fake_get_database():
        raise MongoDBConfigError("MONGODB_CONNECTION_STRING is required before connecting to MongoDB.")

    monkeypatch.setattr("api.routes.judge.get_database", fake_get_database)
    client = TestClient(app)

    response = client.post("/judge/seed-demo-trip")

    assert response.status_code == 503
    assert response.json()["detail"] == {
        "code": "MONGODB_PROVIDER_NOT_CONFIGURED",
        "message": "MONGODB_CONNECTION_STRING is required before connecting to MongoDB.",
    }


def test_judge_seed_returns_503_when_mongodb_provider_is_unavailable():
    class UnavailableCollection(FakeCollection):
        def replace_one(self, query, document, upsert=False):
            raise ServerSelectionTimeoutError("Atlas network access rejected Cloud Run")

    db = FakeDB()
    db.group_trips = UnavailableCollection([])
    install_overrides(db)
    client = TestClient(app)

    response = client.post("/judge/seed-demo-trip")

    assert response.status_code == 503
    assert response.json()["detail"] == {
        "code": "MONGODB_PROVIDER_UNAVAILABLE",
        "message": "Atlas network access rejected Cloud Run",
    }


def test_judge_instructions_returns_plain_text_guide():
    client = TestClient(app)

    response = client.get("/judge/instructions")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    text = response.text
    assert "Bounce Judge Test Mode" in text
    assert "POST /judge/reset" in text
    assert "POST /judge/seed-demo-trip" in text
    assert "POST /judge/trigger-disruption" in text
