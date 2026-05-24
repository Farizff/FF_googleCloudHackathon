from fastapi.testclient import TestClient

from api.main import app
from api.routes import scheduler
from workers.flight_poller import poll_active_trip_flights
from workers.reminder_dispatcher import dispatch_due_reminders


class FakeCollection:
    def __init__(self, records=None):
        self.records = list(records or [])
        self.updated = []
        self.inserted = []

    def find(self, query=None):
        query = query or {}
        return [record for record in self.records if _matches(record, query)]

    def find_one(self, query):
        for record in self.records:
            if _matches(record, query):
                return record
        return None

    def insert_one(self, document):
        self.inserted.append(document)
        self.records.append(document)

    def update_one(self, query, update):
        self.updated.append({"query": query, "update": update})
        for record in self.records:
            if _matches(record, query):
                if "$set" in update:
                    record.update(update["$set"])
                return None
        return None

    def replace_one(self, query, document, upsert=False):
        self.records = [record for record in self.records if not _matches(record, query)]
        if upsert:
            self.records.append(document)


def _matches(record, query):
    for key, expected in query.items():
        actual = record.get(key)
        if isinstance(expected, dict):
            if "$in" in expected and actual not in expected["$in"]:
                return False
            if "$lte" in expected and not (actual is not None and actual <= expected["$lte"]):
                return False
            if "$ne" in expected and actual == expected["$ne"]:
                return False
        elif actual != expected:
            return False
    return True


class FakeDB:
    def __init__(self):
        self.compliance_reminders = FakeCollection(
            [
                {
                    "reminder_id": "rem_visa_priya",
                    "trip_id": "trip_tokyo",
                    "user_id": "u_priya",
                    "name": "Priya",
                    "message": "Japan tourist visa required.",
                    "visibility": "private_to_member",
                    "due_at": "2026-07-01T08:00:00Z",
                    "sent_at": None,
                },
                {
                    "reminder_id": "rem_future",
                    "trip_id": "trip_tokyo",
                    "user_id": "u_alex",
                    "name": "Alex",
                    "message": "Pack comfortable shoes.",
                    "visibility": "private_to_member",
                    "due_at": "2026-07-02T08:00:00Z",
                    "sent_at": None,
                },
                {
                    "reminder_id": "rem_sent",
                    "trip_id": "trip_tokyo",
                    "user_id": "u_rania",
                    "name": "Rania",
                    "message": "Visa reminder already sent.",
                    "visibility": "private_to_member",
                    "due_at": "2026-07-01T07:00:00Z",
                    "sent_at": "2026-07-01T07:05:00Z",
                },
            ]
        )
        self.notification_log = FakeCollection([])
        self.itineraries = FakeCollection(
            [
                {
                    "itinerary_id": "iti_tokyo",
                    "trip_id": "trip_tokyo",
                    "status": "confirmed",
                    "flights": [
                        {
                            "flight_number": "NH106",
                            "departure_date": "2026-07-01",
                            "live_status": "scheduled",
                            "member_ids": ["u_priya"],
                        },
                        {
                            "flight_number": "JL1",
                            "departure_date": "2026-07-03",
                            "live_status": "scheduled",
                            "member_ids": ["u_alex"],
                        },
                    ],
                }
            ]
        )
        self.flight_status_cache = FakeCollection(
            [
                {
                    "flight_number": "NH106",
                    "departure_date": "2026-07-01",
                    "polled_at": "2026-07-01T07:00:00Z",
                    "status": "scheduled",
                    "scheduled_departure": "2026-07-01T11:55:00+09:00",
                    "actual_departure": None,
                    "scheduled_arrival": "2026-07-01T16:50:00+09:00",
                    "actual_arrival": None,
                    "delay_minutes": 0,
                }
            ]
        )


class FakeFlightClient:
    def __init__(self):
        self.calls = []

    def get_flight_by_number(self, flight_number, departure_date):
        self.calls.append({"flight_number": flight_number, "departure_date": departure_date})
        return {
            "status": "delayed" if flight_number == "NH106" else "scheduled",
            "scheduled_departure": "2026-07-01T11:55:00+09:00",
            "actual_departure": "2026-07-01T12:30:00+09:00" if flight_number == "NH106" else None,
            "scheduled_arrival": "2026-07-01T16:50:00+09:00",
            "actual_arrival": None,
            "delay_minutes": 35 if flight_number == "NH106" else 0,
        }


class FakePublisher:
    def __init__(self):
        self.published = []

    def publish(self, topic, message):
        self.published.append({"topic": topic, "message": message})


def test_reminder_dispatcher_sends_due_private_reminders_once():
    db = FakeDB()
    sent_messages = []

    result = dispatch_due_reminders(
        db=db,
        now_iso="2026-07-01T09:00:00Z",
        send_reminder_fn=lambda reminder: sent_messages.append(reminder) or {"message_id": "msg_1"},
    )

    assert result == {"scanned": 3, "sent": 1, "skipped": 2, "failed": 0}
    assert [message["reminder_id"] for message in sent_messages] == ["rem_visa_priya"]
    assert db.compliance_reminders.find_one({"reminder_id": "rem_visa_priya"})["sent_at"] == "2026-07-01T09:00:00Z"
    assert db.notification_log.inserted[0]["trigger_event"] == "compliance_reminder"
    assert db.notification_log.inserted[0]["visibility"] == "private_to_member"


def test_flight_poller_checks_due_flights_and_publishes_status_changes():
    db = FakeDB()
    client = FakeFlightClient()
    publisher = FakePublisher()

    result = poll_active_trip_flights(
        db=db,
        now_iso="2026-07-01T09:00:00Z",
        aerodatabox_client=client,
        pubsub_publisher=publisher,
    )

    assert result == {"itineraries_scanned": 1, "flights_polled": 2, "status_changes": 1}
    assert client.calls == [
        {"flight_number": "NH106", "departure_date": "2026-07-01"},
        {"flight_number": "JL1", "departure_date": "2026-07-03"},
    ]
    assert db.itineraries.find_one({"itinerary_id": "iti_tokyo"})["flights"][0]["live_status"] == "delayed"
    assert publisher.published == [
        {
            "topic": "flight-status-change",
            "message": {
                "flight_number": "NH106",
                "departure_date": "2026-07-01",
                "previous_status": "scheduled",
                "status": "delayed",
                "delay_minutes": 35,
            },
        }
    ]


def test_internal_scheduler_endpoints_trigger_workers_with_injected_dependencies():
    db = FakeDB()
    flight_client = FakeFlightClient()
    publisher = FakePublisher()
    sent_messages = []
    app.dependency_overrides.clear()
    app.dependency_overrides[scheduler.get_db] = lambda: db
    app.dependency_overrides[scheduler.get_now_fn] = lambda: (lambda: "2026-07-01T09:00:00Z")
    app.dependency_overrides[scheduler.get_aerodatabox_client] = lambda: flight_client
    app.dependency_overrides[scheduler.get_pubsub_publisher] = lambda: publisher
    app.dependency_overrides[scheduler.get_send_reminder_fn] = lambda: (lambda reminder: sent_messages.append(reminder) or {"message_id": "msg_1"})
    client = TestClient(app)

    reminders = client.post("/internal/scheduler/reminders")
    flights = client.post("/internal/scheduler/flights")

    assert reminders.status_code == 200
    assert reminders.json() == {"success": True, "result": {"scanned": 3, "sent": 1, "skipped": 2, "failed": 0}}
    assert flights.status_code == 200
    assert flights.json() == {"success": True, "result": {"itineraries_scanned": 1, "flights_polled": 2, "status_changes": 1}}
    assert sent_messages[0]["user_id"] == "u_priya"


def teardown_function():
    app.dependency_overrides.clear()
