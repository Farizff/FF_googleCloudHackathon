from agent.tools.poll_flight_status import poll_flight_status


class FakeCacheCollection:
    def __init__(self, records=None):
        self.records = records or []
        self.find_one_queries = []
        self.replaced = []

    def find_one(self, query):
        self.find_one_queries.append(query)
        for record in self.records:
            if all(record.get(key) == value for key, value in query.items()):
                return record
        return None

    def replace_one(self, query, document, upsert=False):
        self.replaced.append({"query": query, "document": document, "upsert": upsert})
        for index, record in enumerate(self.records):
            if all(record.get(key) == value for key, value in query.items()):
                self.records[index] = document
                return None
        if upsert:
            self.records.append(document)
        return None


class FakeAeroDataBoxClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get_flight_by_number(self, flight_number, departure_date):
        self.calls.append({"flight_number": flight_number, "departure_date": departure_date})
        return self.response


class FakePublisher:
    def __init__(self):
        self.published = []

    def publish(self, topic, message):
        self.published.append({"topic": topic, "message": message})


def status_payload(status="scheduled", actual_departure=None, actual_arrival=None):
    return {
        "status": status,
        "scheduled_departure": "2026-07-01T11:55:00+09:00",
        "actual_departure": actual_departure,
        "scheduled_arrival": "2026-07-01T16:50:00+09:00",
        "actual_arrival": actual_arrival,
        "delay_minutes": 0 if actual_departure is None else 35,
    }


def test_poll_flight_status_returns_fresh_cached_status_without_api_call():
    cached = {
        "flight_number": "NH106",
        "departure_date": "2026-07-01",
        "polled_at": "2026-07-01T09:45:00Z",
        **status_payload(status="en_route", actual_departure="2026-07-01T12:30:00+09:00"),
    }
    cache = FakeCacheCollection([cached])
    client = FakeAeroDataBoxClient(status_payload(status="landed"))
    publisher = FakePublisher()

    result = poll_flight_status(
        flight_number="NH106",
        departure_date="2026-07-01",
        cache_collection=cache,
        aerodatabox_client=client,
        pubsub_publisher=publisher,
        clock=lambda: "2026-07-01T10:00:00Z",
    )

    assert result == {
        "status": "en_route",
        "scheduled_departure": "2026-07-01T11:55:00+09:00",
        "actual_departure": "2026-07-01T12:30:00+09:00",
        "scheduled_arrival": "2026-07-01T16:50:00+09:00",
        "actual_arrival": None,
        "delay_minutes": 35,
    }
    assert client.calls == []
    assert cache.replaced == []
    assert publisher.published == []


def test_poll_flight_status_calls_aerodatabox_and_upserts_stale_cache():
    stale = {
        "flight_number": "NH106",
        "departure_date": "2026-07-01",
        "polled_at": "2026-07-01T09:00:00Z",
        **status_payload(status="scheduled"),
    }
    live = status_payload(status="delayed", actual_departure="2026-07-01T12:30:00+09:00")
    cache = FakeCacheCollection([stale])
    client = FakeAeroDataBoxClient(live)
    publisher = FakePublisher()

    result = poll_flight_status(
        "NH106",
        "2026-07-01",
        cache,
        client,
        publisher,
        clock=lambda: "2026-07-01T10:00:00Z",
    )

    assert result == live
    assert client.calls == [{"flight_number": "NH106", "departure_date": "2026-07-01"}]
    assert cache.replaced == [
        {
            "query": {"flight_number": "NH106", "departure_date": "2026-07-01"},
            "document": {
                "flight_number": "NH106",
                "departure_date": "2026-07-01",
                "polled_at": "2026-07-01T10:00:00Z",
                **live,
            },
            "upsert": True,
        }
    ]


def test_poll_flight_status_publishes_when_status_changes():
    cache = FakeCacheCollection(
        [
            {
                "flight_number": "NH106",
                "departure_date": "2026-07-01",
                "polled_at": "2026-07-01T09:00:00Z",
                **status_payload(status="scheduled"),
            }
        ]
    )
    live = status_payload(status="cancelled")
    publisher = FakePublisher()

    poll_flight_status(
        "NH106",
        "2026-07-01",
        cache,
        FakeAeroDataBoxClient(live),
        publisher,
        clock=lambda: "2026-07-01T10:00:00Z",
    )

    assert publisher.published == [
        {
            "topic": "flight-status-change",
            "message": {
                "flight_number": "NH106",
                "departure_date": "2026-07-01",
                "previous_status": "scheduled",
                "status": "cancelled",
                "delay_minutes": 0,
            },
        }
    ]


def test_poll_flight_status_does_not_publish_for_initial_cache_miss():
    cache = FakeCacheCollection([])
    publisher = FakePublisher()

    poll_flight_status(
        "NH106",
        "2026-07-01",
        cache,
        FakeAeroDataBoxClient(status_payload(status="scheduled")),
        publisher,
        clock=lambda: "2026-07-01T10:00:00Z",
    )

    assert publisher.published == []


def test_poll_flight_status_normalizes_aerodatabox_shape():
    response = [
        {
            "status": "Arrived",
            "departure": {
                "scheduledTime": {"local": "2026-07-01 11:55+09:00"},
                "actualTime": {"local": "2026-07-01 12:05+09:00"},
                "delayMinutes": 10,
            },
            "arrival": {
                "scheduledTime": {"local": "2026-07-01 16:50+09:00"},
                "actualTime": {"local": "2026-07-01 17:05+09:00"},
            },
        }
    ]

    result = poll_flight_status(
        "NH106",
        "2026-07-01",
        FakeCacheCollection([]),
        FakeAeroDataBoxClient(response),
        FakePublisher(),
        clock=lambda: "2026-07-01T10:00:00Z",
    )

    assert result == {
        "status": "arrived",
        "scheduled_departure": "2026-07-01 11:55+09:00",
        "actual_departure": "2026-07-01 12:05+09:00",
        "scheduled_arrival": "2026-07-01 16:50+09:00",
        "actual_arrival": "2026-07-01 17:05+09:00",
        "delay_minutes": 10,
    }
