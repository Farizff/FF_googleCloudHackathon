from fastapi.testclient import TestClient

from api.main import app
from api.routes import chat


class FakePlanner:
    def __init__(self):
        self.calls = []

    def plan(self, request):
        self.calls.append(request)
        return chat.PlanningResult(
            message="I can help plan that Tokyo reunion. I’ll start with dates, group size, and budget, then build the first itinerary path.",
            intent="full_trip_planning",
            trip_id=request.trip_id or "trip_draft_u_alex",
            actions=["classify_intent", "start_planning_response"],
        )


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


def install_overrides(planner=None, publisher=None, now=1000.0):
    app.dependency_overrides.clear()
    chat.rate_buckets.clear()
    fake_planner = planner or FakePlanner()
    fake_publisher = publisher or FakePublisher()
    app.dependency_overrides[chat.get_planner] = lambda: fake_planner
    app.dependency_overrides[chat.get_chat_publisher] = lambda: fake_publisher
    app.dependency_overrides[chat.get_time_fn] = lambda: (lambda: now)
    return fake_planner, fake_publisher


def teardown_function():
    app.dependency_overrides.clear()
    chat.rate_buckets.clear()


def test_chat_accepts_natural_language_trip_entry_and_publishes_planning_response_path():
    planner, publisher = install_overrides()
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={
            "user_id": "u_alex",
            "message": "Plan a 7 day Tokyo reunion for 10 friends in July with food, culture, and one slower day.",
            "trip_id": "trip_tokyo_reunion_2026",
            "role": "organiser",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["intent"] == "full_trip_planning"
    assert body["trip_id"] == "trip_tokyo_reunion_2026"
    assert body["planning_response_path"].startswith("/trips/trip_tokyo_reunion_2026/threads/main/")
    assert body["loading_states"] == [
        "reading_group_context",
        "classifying_intent",
        "planning_next_step",
        "publishing_response",
    ]
    assert "Tokyo reunion" in body["message"]
    assert planner.calls[0].message.startswith("Plan a 7 day Tokyo reunion")
    assert publisher.messages[0]["role"] == "assistant"
    assert publisher.messages[0]["author_id"] == "bounce"


def test_chat_blocks_pii_without_calling_planner_or_publisher():
    planner, publisher = install_overrides()
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={"user_id": "u_alex", "message": "My passport number is A12345678, please store it."},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "PII_DETECTED",
            "pii_type": "passport_number",
            "message": "Heads up — I don't need or store that. Let's continue without it.",
        }
    }
    assert planner.calls == []
    assert publisher.messages == []


def test_chat_rate_limits_after_five_messages_per_user_per_ten_seconds():
    install_overrides(now=2000.0)
    client = TestClient(app)

    for _ in range(5):
        response = client.post("/chat", json={"user_id": "u_alex", "message": "Add one ramen dinner."})
        assert response.status_code == 200

    limited = client.post("/chat", json={"user_id": "u_alex", "message": "And add a museum."})

    assert limited.status_code == 429
    assert limited.json() == {
        "detail": {
            "code": "RATE_LIMITED",
            "message": "Please slow down — Bounce chat allows 5 messages every 10 seconds per user.",
        }
    }


def test_chat_maps_planner_failure_to_user_safe_error():
    class FailingPlanner:
        def plan(self, request):
            raise chat.PlanningError("AGENT_UNAVAILABLE", "Agent Builder is not configured yet.")

    install_overrides(planner=FailingPlanner())
    client = TestClient(app)

    response = client.post("/chat", json={"user_id": "u_alex", "message": "Plan Tokyo."})

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "AGENT_UNAVAILABLE",
            "message": "I can’t reach the planning brain right now. Please try again in a moment.",
        }
    }
