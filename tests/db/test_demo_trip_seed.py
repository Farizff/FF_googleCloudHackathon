import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parents[2] / "db" / "seed" / "seed_demo_trip.json"

EXPECTED_MEMBERS = {
    "Alex Chen": {"origin": "SFO", "passport": "USA", "role": "organiser", "visa_required": False},
    "Priya Patel": {"origin": "SFO", "passport": "IND", "role": "co_leader", "visa_required": True},
    "Marcus Johnson": {"origin": "SFO", "passport": "USA", "role": "member", "visa_required": False},
    "Sofia Gutierrez": {"origin": "LAX", "passport": "MEX", "role": "member", "visa_required": False},
    "Jake Kim": {"origin": "LAX", "passport": "KOR", "role": "member", "visa_required": False},
    "Aditya Sharma": {"origin": "JFK", "passport": "IND", "role": "member", "visa_required": True},
    "Emma Clarke": {"origin": "JFK", "passport": "GBR", "role": "member", "visa_required": False},
    "Carlos Mendez": {"origin": "SEA", "passport": "BRA", "role": "member", "visa_required": False},
    "Liam Murphy": {"origin": "SEA", "passport": "IRL", "role": "member", "visa_required": False},
    "Rania Hassan": {"origin": "ORD", "passport": "EGY", "role": "member", "visa_required": True},
}


def load_seed() -> dict:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def members_by_name(seed: dict) -> dict:
    return {member["name"]: member for member in seed["traveller_profiles"]}


def test_demo_trip_seed_contains_the_reunion_group_with_prd_nationality_diversity():
    """The demo group must be multinational so visa reminders are testable."""
    seed = load_seed()
    members = members_by_name(seed)

    assert seed["group_trip"]["trip_name"] == "The Tokyo Reunion"
    assert seed["group_trip"]["destination_iata"] == "NRT"
    assert set(members) == set(EXPECTED_MEMBERS)
    assert len(members) == 10

    passports = {member["passport_country"] for member in members.values()}
    assert len(passports) >= 5
    assert passports == {"USA", "IND", "MEX", "KOR", "GBR", "BRA", "IRL", "EGY"}

    for name, expected in EXPECTED_MEMBERS.items():
        member = members[name]
        assert member["home_city_iata"] == expected["origin"]
        assert member["passport_country"] == expected["passport"]
        assert member["nationality"] == expected["passport"]
        assert member["japan_visa_required"] is expected["visa_required"]


def test_demo_group_roles_and_private_compliance_flags_match_prd():
    """Only admins get admin roles; visa nudges remain private per member."""
    seed = load_seed()
    members = members_by_name(seed)
    group_members = {member["user_id"]: member for member in seed["group_trip"]["members"]}

    roles = {group_members[member["user_id"]]["role"] for member in members.values()}
    assert roles == {"organiser", "co_leader", "member"}
    assert group_members[members["Alex Chen"]["user_id"]]["role"] == "organiser"
    assert group_members[members["Priya Patel"]["user_id"]]["role"] == "co_leader"

    visa_names = {name for name, member in members.items() if member["japan_visa_required"]}
    assert visa_names == {"Priya Patel", "Aditya Sharma", "Rania Hassan"}

    assert "compliance_status" not in seed["group_trip"]
    assert "visa_status" not in seed["group_trip"]
    for group_member in seed["group_trip"]["members"]:
        assert group_member["shares_compliance_with_admins"] is False


def test_demo_flockmode_seed_matches_prd_day_5_assignment():
    """Day 5 FlockMode must be deterministic for the judge demo path."""
    seed = load_seed()
    flocks = {flock["flock_name"]: flock for flock in seed["flock_mode"]["flocks"]}

    assert seed["flock_mode"]["day_number"] == 5
    assert seed["flock_mode"]["reconvene_time"] == "18:30"
    assert seed["flock_mode"]["reconvene_location"] == "Shinjuku Station East Exit"
    assert set(flocks) == {"The Explorers", "The Foodies", "The Shoppers"}

    assert flocks["The Explorers"]["leader_name"] == "Priya Patel"
    assert flocks["The Explorers"]["member_names"] == ["Alex Chen", "Priya Patel", "Aditya Sharma", "Emma Clarke"]
    assert flocks["The Foodies"]["leader_name"] == "Marcus Johnson"
    assert flocks["The Foodies"]["member_names"] == ["Marcus Johnson", "Sofia Gutierrez", "Liam Murphy"]
    assert flocks["The Shoppers"]["leader_name"] == "Jake Kim"
    assert flocks["The Shoppers"]["member_names"] == ["Jake Kim", "Carlos Mendez", "Rania Hassan"]
