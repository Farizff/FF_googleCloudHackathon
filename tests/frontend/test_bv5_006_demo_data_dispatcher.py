import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOTYPE = ROOT / "frontend" / "bounce_v5_prototype.html"
CONTRACT = ROOT / "docs" / "kanban" / "bounce_v5_contract.md"


def html_text():
    return PROTOTYPE.read_text(encoding="utf-8")


def script_text():
    match = re.search(r"<script>(.*?)</script>", html_text(), re.S)
    assert match, "prototype should keep JS inline"
    return match.group(1)


def test_demo_data_matches_prd_v5_five_trip_ids_and_core_fields():
    script = script_text()
    for marker in [
        "id: 'lisbon-bday'",
        "name: \"Maya's 30th\"",
        "city: 'Lisbon'",
        "country: 'Portugal'",
        "dates: 'Jul 12 – Jul 17, 2025'",
        "state: 'planning'",
        "daysToGo: 48",
        "totalDays: 6",
        "currency: 'EUR'",
        "id: 'reunion-tk26'",
        "name: 'The Reunion'",
        "city: 'Tokyo'",
        "country: 'Japan'",
        "dates: 'Oct 15 – Oct 21, 2026'",
        "state: 'active'",
        "activeDay: 3",
        "totalDays: 7",
        "id: 'cdmx-reunion'",
        "id: 'seoul-food-crawl'",
        "id: 'lisbon-long-weekend'",
    ]:
        assert marker in script

    assert "lisbon_planning" not in script
    assert "tokyo_active" not in script
    assert "seoul_past" not in script


def test_demo_data_includes_prd_members_and_local_currency_wrap_data():
    script = script_text()
    for member in ["maya", "sofiaA", "priyaN", "chloe", "zara", "alex", "marcus", "aditya", "emma", "carlos", "liam", "rania"]:
        assert member in script

    for marker in [
        "'cdmx-reunion':",
        "currency: 'MXN'",
        "total: 'MX$37,000'",
        "perPerson: 'MX$9,250/person'",
        "'seoul-food-crawl':",
        "currency: 'KRW'",
        "total: '₩5,900,000'",
        "perPerson: '₩983,000/person'",
        "'lisbon-long-weekend':",
        "total: '€1,160'",
        "perPerson: '€290/person'",
    ]:
        assert marker in script

    assert "USD" not in script


def test_phase_dispatcher_uses_trip_state_and_hash_route_params():
    script = script_text()
    for marker in [
        "function parseHashRoute()",
        "new URLSearchParams",
        "screen=X&phase=Y&user=Z",
        "function phaseForTrip(trip)",
        "if (trip.state === 'planning') return 'planning-itinerary';",
        "if (trip.state === 'active') return 'active-today';",
        "if (trip.state === 'past') return 'wrap';",
        "function routeToTrip(trip)",
        "window.location.hash",
        "hashchange",
    ]:
        assert marker in script


def test_home_sections_are_derived_from_trip_state():
    script = script_text()
    assert "const upcoming = DEMO_TRIPS.filter((trip) => trip.state === 'planning');" in script
    assert "const active = DEMO_TRIPS.filter((trip) => trip.state === 'active');" in script
    assert "const past = DEMO_TRIPS.filter((trip) => trip.state === 'past');" in script
    assert "In planning" in script
    assert "● Day" in script
    assert "⭐" in script


def test_bv5_contract_marks_demo_data_done_and_points_to_home_entry():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-006 — Implement v5 demo data and phase dispatcher**" in contract
    assert "Recommended next action: **BV5-007 — Build Home and Entry Conversation screens**" in contract
