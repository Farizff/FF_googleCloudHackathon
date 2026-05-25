from fastapi.testclient import TestClient

from api.main import app
from api.routes import flights, flight_status, group, itinerary, trip


class FakeCollection:
    def __init__(self, records=None):
        self.records = list(records or [])
        self.inserted = []
        self.replaced = []
        self.updated = []

    def find_one(self, query):
        for record in self.records:
            if _matches(record, query):
                return record
        return None

    def find(self, query):
        return [record for record in self.records if _matches(record, query)]

    def insert_one(self, document):
        self.inserted.append(document)
        self.records.append(document)

    def replace_one(self, query, document, upsert=False):
        self.replaced.append({"query": query, "document": document, "upsert": upsert})
        self.records = [record for record in self.records if not _matches(record, query)]
        if upsert:
            self.records.append(document)

    def update_one(self, query, update):
        self.updated.append({"query": query, "update": update})
        for record in self.records:
            if _matches(record, query):
                if "$set" in update:
                    record.update(update["$set"])
                if "$push" in update:
                    for key, value in update["$push"].items():
                        record.setdefault(key, []).append(value)
                return


def _matches(record, query):
    for key, expected in query.items():
        actual = record.get(key)
        if actual != expected:
            return False
    return True


class FakeDB:
    def __init__(self):
        self.group_trips = FakeCollection(
            [
                {
                    "trip_id": "trip_tokyo",
                    "group_type": "friends",
                    "status": "planning",
                    "destination_city": "Tokyo",
                    "destination_country": "Japan",
                    "destination_iata": "TYO",
                    "members": [
                        {"user_id": "u_alex", "name": "Alex", "role": "organiser"},
                        {"user_id": "u_priya", "name": "Priya", "role": "member"},
                    ],
                }
            ]
        )
        self.itineraries = FakeCollection(
            [
                {
                    "itinerary_id": "iti_tokyo",
                    "_id": object(),
                    "trip_id": "trip_tokyo",
                    "status": "draft",
                    "days": [],
                    "flights": [
                        {
                            "flight_number": "UA837",
                            "airline_iata": "UA",
                            "origin_iata": "SFO",
                            "destination_iata": "NRT",
                            "member_ids": ["u_alex"],
                            "risk_score": 42,
                            "risk_tier": "moderate",
                            "option_tier": "recommended",
                            "live_status": "scheduled",
                        }
                    ],
                }
            ]
        )
        self.flight_status_events = FakeCollection([])
        self.invite_tokens = FakeCollection([])
        self.suggestions = FakeCollection([])


def install_overrides(db=None):
    app.dependency_overrides.clear()
    fake_db = db or FakeDB()

    def override_db():
        return fake_db

    for provider in [trip.get_db, itinerary.get_db, flights.get_db, flight_status.get_db, group.get_db]:
        app.dependency_overrides[provider] = override_db
    app.dependency_overrides[trip.get_id_fn] = lambda: (lambda prefix: f"{prefix}_fixed")
    app.dependency_overrides[itinerary.get_id_fn] = lambda: (lambda prefix: f"{prefix}_fixed")
    app.dependency_overrides[group.get_now_fn] = lambda: (lambda: "2026-07-04T09:00:00Z")
    app.dependency_overrides[flight_status.get_now_fn] = lambda: (lambda: "2026-07-04T09:00:00Z")
    return fake_db


def teardown_function():
    app.dependency_overrides.clear()


def test_create_and_get_trip_use_prd_group_trip_shape():
    db = install_overrides(FakeDB())
    client = TestClient(app)

    created = client.post(
        "/trips",
        json={
            "group_type": "friends",
            "trip_mode": "international",
            "destination_city": "Kyoto",
            "destination_country": "Japan",
            "destination_iata": "KIX",
            "organiser": {"user_id": "u_alex", "name": "Alex", "origin_city_iata": "SFO"},
        },
    )

    assert created.status_code == 200
    body = created.json()
    assert body["success"] is True
    assert body["trip"]["trip_id"] == "trip_fixed"
    assert body["trip"]["status"] == "planning"
    assert body["trip"]["members"][0]["role"] == "organiser"
    assert db.group_trips.inserted[0]["destination_iata"] == "KIX"

    fetched = client.get("/trips/trip_fixed")
    assert fetched.status_code == 200
    assert fetched.json()["trip"]["destination_city"] == "Kyoto"


def test_itinerary_create_get_and_status_update_are_route_wrapped():
    db = install_overrides(FakeDB())
    client = TestClient(app)

    created = client.post("/itineraries", json={"trip_id": "trip_tokyo", "days": [{"day_number": 1, "shared_schedule": []}]})

    assert created.status_code == 200
    itinerary_body = created.json()["itinerary"]
    assert itinerary_body["itinerary_id"] == "itinerary_fixed"
    assert itinerary_body["status"] == "draft"
    assert db.itineraries.inserted[0]["trip_id"] == "trip_tokyo"

    updated = client.patch("/itineraries/itinerary_fixed/status", json={"status": "confirmed"})
    assert updated.status_code == 200
    assert updated.json() == {"success": True, "itinerary_id": "itinerary_fixed", "status": "confirmed"}

    fetched = client.get("/itineraries/itinerary_fixed")
    assert fetched.status_code == 200
    assert fetched.json()["itinerary"]["status"] == "confirmed"

    fetched_seed = client.get("/itineraries/iti_tokyo")
    assert fetched_seed.status_code == 200
    assert "_id" not in fetched_seed.json()["itinerary"]


def test_flights_list_and_attach_selected_flight_to_itinerary():
    db = install_overrides(FakeDB())
    client = TestClient(app)

    listed = client.get("/trips/trip_tokyo/flights")
    assert listed.status_code == 200
    assert listed.json()["flights"][0]["flight_number"] == "UA837"

    attached = client.post(
        "/itineraries/iti_tokyo/flights",
        json={
            "flight_number": "JL1",
            "airline_iata": "JL",
            "origin_iata": "SFO",
            "destination_iata": "HND",
            "member_ids": ["u_priya"],
            "risk_score": 20,
            "risk_tier": "low",
            "option_tier": "premium",
        },
    )

    assert attached.status_code == 200
    assert attached.json()["flight"]["live_status"] == "unknown"
    assert db.itineraries.updated[-1]["update"]["$push"]["flights"]["flight_number"] == "JL1"


def test_flight_status_update_records_event_and_updates_matching_flight():
    db = install_overrides(FakeDB())
    client = TestClient(app)

    response = client.patch(
        "/flight-status/iti_tokyo/UA837",
        json={"live_status": "delayed", "status_note": "Delayed 45 minutes"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "itinerary_id": "iti_tokyo",
        "flight_number": "UA837",
        "live_status": "delayed",
    }
    assert db.flight_status_events.inserted[0]["status_note"] == "Delayed 45 minutes"
    assert db.itineraries.find_one({"itinerary_id": "iti_tokyo"})["flights"][0]["live_status"] == "delayed"


def test_group_member_role_changes_respect_prd_governance_boundaries():
    db = install_overrides(FakeDB())
    client = TestClient(app)

    added = client.post("/trips/trip_tokyo/members", json={"user_id": "u_carlos", "name": "Carlos", "role": "member"})
    assert added.status_code == 200
    assert added.json()["member"]["profile_complete"] is False

    promoted = client.patch("/trips/trip_tokyo/members/u_carlos/role", json={"role": "co_leader", "actor_user_id": "u_alex"})
    assert promoted.status_code == 200
    assert promoted.json()["member"]["role"] == "co_leader"

    forbidden = client.patch("/trips/trip_tokyo/members/u_alex/role", json={"role": "member", "actor_user_id": "u_carlos"})
    assert forbidden.status_code == 403
    assert forbidden.json()["detail"]["code"] == "ORGANISER_ROLE_LOCKED"


def test_simple_trip_invite_token_is_immediately_joinable():
    db = install_overrides(FakeDB())
    client = TestClient(app)

    created = client.post(
        "/trips/simple",
        json={
            "user_id": "u_alex",
            "name": "Alex",
            "destination_city": "Tokyo",
            "destination_country": "Japan",
            "destination_iata": "NRT",
            "origin_city_iata": "SFO",
        },
    )

    assert created.status_code == 200
    body = created.json()
    assert body["trip"]["invite_token"] == "invite_fixed"
    assert db.invite_tokens.find_one({"token": "invite_fixed", "status": "active"}) == {
        "token": "invite_fixed",
        "trip_id": "trip_fixed",
        "role": "member",
        "status": "active",
    }

    joined = client.post(
        "/trips/join",
        json={"invite_token": "invite_fixed", "user_id": "u_priya", "name": "Priya", "origin_city_iata": "SIN"},
    )

    assert joined.status_code == 200
    assert joined.json()["trip_id"] == "trip_fixed"
    assert db.group_trips.find_one({"trip_id": "trip_fixed"})["members"][-1]["user_id"] == "u_priya"
