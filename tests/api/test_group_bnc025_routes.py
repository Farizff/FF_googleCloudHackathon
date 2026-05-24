from fastapi.testclient import TestClient

from api.main import app
from tests.api.test_trip_itinerary_flights_group_routes import FakeDB, install_overrides


def teardown_function():
    app.dependency_overrides.clear()


def test_invites_require_admin_and_acceptance_adds_member_with_token_role():
    db = install_overrides(FakeDB())
    client = TestClient(app)

    denied = client.post("/trips/trip_tokyo/invites", json={"actor_user_id": "u_priya", "role": "member"})
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "INVITE_FORBIDDEN"

    created = client.post("/trips/trip_tokyo/invites", json={"actor_user_id": "u_alex", "role": "co_leader"})
    assert created.status_code == 200
    invite = created.json()["invite"]
    assert invite["trip_id"] == "trip_tokyo"
    assert invite["role"] == "co_leader"
    assert invite["token"]
    assert db.invite_tokens.inserted[0]["created_by_user_id"] == "u_alex"

    accepted = client.post(
        f"/trips/trip_tokyo/invites/{invite['token']}/accept",
        json={"user_id": "u_emma", "name": "Emma", "origin_city_iata": "SEA"},
    )
    assert accepted.status_code == 200
    assert accepted.json()["member"]["role"] == "co_leader"
    assert db.group_trips.find_one({"trip_id": "trip_tokyo"})["members"][-1]["user_id"] == "u_emma"


def test_co_leader_cap_is_two_and_members_cannot_apply_suggestions_directly():
    db = install_overrides(FakeDB())
    client = TestClient(app)

    first = client.patch("/trips/trip_tokyo/members/u_priya/role", json={"role": "co_leader", "actor_user_id": "u_alex"})
    assert first.status_code == 200
    added = client.post("/trips/trip_tokyo/members", json={"user_id": "u_marcus", "name": "Marcus", "role": "member"})
    assert added.status_code == 200
    second = client.patch("/trips/trip_tokyo/members/u_marcus/role", json={"role": "co_leader", "actor_user_id": "u_alex"})
    assert second.status_code == 200
    added2 = client.post("/trips/trip_tokyo/members", json={"user_id": "u_sofia", "name": "Sofia", "role": "member"})
    assert added2.status_code == 200

    capped = client.patch("/trips/trip_tokyo/members/u_sofia/role", json={"role": "co_leader", "actor_user_id": "u_alex"})
    assert capped.status_code == 403
    assert capped.json()["detail"]["code"] == "CO_LEADER_LIMIT_REACHED"

    suggestion = client.post(
        "/trips/trip_tokyo/suggestions",
        json={"submitted_by_user_id": "u_sofia", "target_scope": "main_trip", "message": "Can we add more ramen stops?"},
    )
    assert suggestion.status_code == 200
    assert suggestion.json()["suggestion"]["status"] == "pending"
    assert db.suggestions.inserted[0]["target_scope"] == "main_trip"

    member_review = client.patch(
        f"/trips/trip_tokyo/suggestions/{suggestion.json()['suggestion']['suggestion_id']}/review",
        json={"actor_user_id": "u_sofia", "status": "accepted", "admin_note": "Approved"},
    )
    assert member_review.status_code == 403
    assert member_review.json()["detail"]["code"] == "SUGGESTION_REVIEW_FORBIDDEN"

    admin_review = client.patch(
        f"/trips/trip_tokyo/suggestions/{suggestion.json()['suggestion']['suggestion_id']}/review",
        json={"actor_user_id": "u_alex", "status": "accepted", "admin_note": "Good idea"},
    )
    assert admin_review.status_code == 200
    assert admin_review.json()["suggestion"]["status"] == "accepted"


def test_flockmode_permissions_chat_paths_and_flock_leader_scope():
    db = install_overrides(FakeDB())
    db.itineraries.records[0]["days"] = [{"day_number": 5, "flock_mode_active": False, "flocks": [], "shared_schedule": []}]
    client = TestClient(app)

    member_start = client.post("/trips/trip_tokyo/itineraries/iti_tokyo/days/5/flock-mode/start", json={"actor_user_id": "u_priya", "start_time": "13:00"})
    assert member_start.status_code == 403
    assert member_start.json()["detail"]["code"] == "FLOCK_MODE_ORGANISER_ONLY"

    started = client.post("/trips/trip_tokyo/itineraries/iti_tokyo/days/5/flock-mode/start", json={"actor_user_id": "u_alex", "start_time": "13:00"})
    assert started.status_code == 200
    assert started.json()["day"]["flock_mode_active"] is True

    created = client.post(
        "/trips/trip_tokyo/itineraries/iti_tokyo/days/5/flocks",
        json={
            "actor_user_id": "u_alex",
            "flock_name": "The Explorers",
            "flock_leader_user_id": "u_priya",
            "member_ids": ["u_alex", "u_priya"],
            "schedule": [{"venue_name": "teamLab Borderless"}],
            "reconvene_time": "18:30",
            "reconvene_location": "Shinjuku Station East Exit",
            "reconvene_coordinates": {"lat": 35.6909, "lng": 139.7003},
        },
    )
    assert created.status_code == 200
    flock = created.json()["flock"]
    assert flock["chat_thread_path"] == f"/trips/trip_tokyo/threads/flocks/{flock['flock_id']}"

    leader_patch = client.patch(
        f"/trips/trip_tokyo/itineraries/iti_tokyo/days/5/flocks/{flock['flock_id']}",
        json={"actor_user_id": "u_priya", "schedule": [{"venue_name": "teamLab Planets"}]},
    )
    assert leader_patch.status_code == 200
    assert leader_patch.json()["flock"]["schedule"][0]["venue_name"] == "teamLab Planets"

    organiser_patch = client.patch(
        f"/trips/trip_tokyo/itineraries/iti_tokyo/days/5/flocks/{flock['flock_id']}",
        json={"actor_user_id": "u_alex", "flock_name": "Renamed by organiser"},
    )
    assert organiser_patch.status_code == 200

    ended_by_member = client.post("/trips/trip_tokyo/itineraries/iti_tokyo/days/5/flock-mode/end", json={"actor_user_id": "u_priya", "end_time": "18:30"})
    assert ended_by_member.status_code == 403
    assert ended_by_member.json()["detail"]["code"] == "FLOCK_MODE_ORGANISER_ONLY"


def test_join_trip_via_invite_token():
    """POST /trips/join allows a user to join a trip with a valid invite token."""
    db = install_overrides(FakeDB())
    client = TestClient(app)

    # First create an invite for trip_tokyo (organiser creates invite for a new member role)
    created = client.post("/trips/trip_tokyo/invites", json={"actor_user_id": "u_alex", "role": "member"})
    assert created.status_code == 200
    invite = created.json()["invite"]
    invite_token = invite["token"]
    assert invite["trip_id"] == "trip_tokyo"
    assert invite["status"] == "active"

    # Accept the invite via POST /trips/join
    joined = client.post("/trips/join", json={
        "invite_token": invite_token,
        "user_id": "u_emma",
        "name": "Emma",
        "origin_city_iata": "SEA",
    })
    assert joined.status_code == 200
    result = joined.json()
    assert result["success"] is True
    assert result["trip_id"] == "trip_tokyo"

    # Verify Emma was added as a member
    trip = db.group_trips.find_one({"trip_id": "trip_tokyo"})
    emma = next((m for m in trip["members"] if m["user_id"] == "u_emma"), None)
    assert emma is not None
    assert emma["name"] == "Emma"
    assert emma["role"] == "member"
    assert emma["origin_city_iata"] == "SEA"


def test_join_trip_with_invalid_token_returns_404():
    """POST /trips/join with an unknown token returns INVITE_NOT_FOUND."""
    db = install_overrides(FakeDB())
    client = TestClient(app)

    response = client.post("/trips/join", json={
        "invite_token": "invalid_token_xyz",
        "user_id": "u_emma",
        "name": "Emma",
    })
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "INVITE_NOT_FOUND"


def test_join_trip_already_member_returns_409():
    """POST /trips/join when user is already a member returns MEMBER_ALREADY_EXISTS."""
    db = install_overrides(FakeDB())
    client = TestClient(app)

    # Create invite and join
    created = client.post("/trips/trip_tokyo/invites", json={"actor_user_id": "u_alex", "role": "member"})
    invite_token = created.json()["invite"]["token"]

    joined = client.post("/trips/join", json={
        "invite_token": invite_token,
        "user_id": "u_priya",  # already a member
        "name": "Priya",
    })
    assert joined.status_code == 409
    assert joined.json()["detail"]["code"] == "MEMBER_ALREADY_EXISTS"
