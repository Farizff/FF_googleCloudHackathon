"""Tests for POST /flocks, GET /flocks?trip_id=X, and GET /flocks/{flock_id}."""
from fastapi.testclient import TestClient

from api.main import app


class FakeCollection:
    def __init__(self, records=None):
        self.records = records or []
        self.find_queries = []
        self.find_one_queries = []
        self.inserted = []

    def find(self, query):
        self.find_queries.append(query)
        return [record for record in self.records if all(record.get(k) == v for k, v in query.items())]

    def find_one(self, query):
        self.find_one_queries.append(query)
        for record in self.records:
            if all(record.get(k) == v for k, v in query.items()):
                return record
        return None

    def insert_one(self, document):
        self.inserted.append(document)
        self.records.append(document)
        return None


class FakeDB:
    def __init__(self, trips=None, flocks=None):
        self.group_trips = FakeCollection(trips or [])
        self.flocks = FakeCollection(flocks or [])


def _override_get_db(db):
    from api.routes.flocks import get_db as flocks_get_db
    app.dependency_overrides[flocks_get_db] = lambda: db


def _clear_overrides():
    app.dependency_overrides.clear()


def test_create_flock_success():
    db = FakeDB(trips=[{"trip_id": "trip_tokyo", "members": ["u_alex", "u_priya"]}])
    _override_get_db(db)
    client = TestClient(app)

    payload = {
        "flock_name": "The Explorers",
        "leader_user_id": "u_alex",
        "member_ids": ["u_alex", "u_priya"],
        "trip_id": "trip_tokyo",
        "reconvene_time": "18:30",
        "reconvene_location": "Shinjuku Station East Exit",
        "day_number": 5,
        "activity": "teamLab Borderless",
    }
    response = client.post("/flocks", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["flock_name"] == "The Explorers"
    assert data["leader_user_id"] == "u_alex"
    assert data["member_ids"] == ["u_alex", "u_priya"]
    assert data["trip_id"] == "trip_tokyo"
    assert data["reconvene_time"] == "18:30"
    assert data["reconvene_location"] == "Shinjuku Station East Exit"
    assert data["flock_id"].startswith("flock_")
    assert len(db.flocks.inserted) == 1

    _clear_overrides()


def test_create_flock_trip_not_found():
    db = FakeDB(trips=[])
    _override_get_db(db)
    client = TestClient(app)

    payload = {
        "flock_name": "Orphans",
        "leader_user_id": "u_alex",
        "member_ids": ["u_alex"],
        "trip_id": "nonexistent",
        "reconvene_time": "18:30",
        "reconvene_location": "Nowhere",
    }
    response = client.post("/flocks", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "TRIP_NOT_FOUND"

    _clear_overrides()


def test_list_flocks_returns_all_for_trip():
    db = FakeDB(
        trips=[{"trip_id": "trip_tokyo"}],
        flocks=[
            {"flock_id": "flock_1", "trip_id": "trip_tokyo", "flock_name": "The Explorers", "leader_user_id": "u_alex", "member_ids": ["u_alex"]},
            {"flock_id": "flock_2", "trip_id": "trip_tokyo", "flock_name": "The Foodies", "leader_user_id": "u_marcus", "member_ids": ["u_marcus"]},
            {"flock_id": "flock_other", "trip_id": "other_trip", "flock_name": "Other Flock", "leader_user_id": "u_jake", "member_ids": ["u_jake"]},
        ],
    )
    _override_get_db(db)
    client = TestClient(app)

    response = client.get("/flocks?trip_id=trip_tokyo")

    assert response.status_code == 200
    flocks = response.json()
    assert len(flocks) == 2
    assert all(f["trip_id"] == "trip_tokyo" for f in flocks)

    _clear_overrides()


def test_list_flocks_empty_for_trip_with_no_flocks():
    db = FakeDB(trips=[{"trip_id": "trip_tokyo"}], flocks=[])
    _override_get_db(db)
    client = TestClient(app)

    response = client.get("/flocks?trip_id=trip_tokyo")

    assert response.status_code == 200
    assert response.json() == []

    _clear_overrides()


def test_get_flock_by_id_success():
    db = FakeDB(
        flocks=[
            {
                "flock_id": "flock_explorers",
                "trip_id": "trip_tokyo",
                "flock_name": "The Explorers",
                "leader_user_id": "u_priya",
                "member_ids": ["u_alex", "u_priya", "u_emma"],
                "reconvene_time": "18:30",
                "reconvene_location": "Shinjuku Station",
                "reconvene_coordinates": {"lat": 35.6909, "lng": 139.7016},
                "day_number": 5,
                "activity": "teamLab Borderless",
            }
        ]
    )
    _override_get_db(db)
    client = TestClient(app)

    response = client.get("/flocks/flock_explorers")

    assert response.status_code == 200
    data = response.json()
    assert data["flock_id"] == "flock_explorers"
    assert data["flock_name"] == "The Explorers"
    assert data["member_ids"] == ["u_alex", "u_priya", "u_emma"]

    _clear_overrides()


def test_get_flock_not_found():
    db = FakeDB(flocks=[])
    _override_get_db(db)
    client = TestClient(app)

    response = client.get("/flocks/flock_nonexistent")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "FLOCK_NOT_FOUND"

    _clear_overrides()