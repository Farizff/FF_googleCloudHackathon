import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOTYPE = ROOT / "frontend" / "bounce_v5_prototype.html"
CONTRACT = ROOT / "docs" / "kanban" / "bounce_v5_contract.md"


def html_text():
    return PROTOTYPE.read_text(encoding="utf-8")


def script_text():
    match = re.search(r"<script>(.*?)</script>", html_text(), re.S)
    assert match, "prototype keeps JS inline"
    return match.group(1)


def style_text():
    match = re.search(r"<style>(.*?)</style>", html_text(), re.S)
    assert match, "prototype keeps CSS inline"
    return match.group(1)


def test_global_nav_has_required_items_and_profile_user_pill():
    script = script_text()
    for label in ["Home", "Plan a new trip", "Join a trip"]:
        assert label in script

    assert "renderGlobalNav" in script
    assert "renderUserPill" in script
    assert "user-pill" in script
    assert "setPhase('profile')" in script
    assert "Fariz" in script


def test_trip_scoped_nav_is_phase_aware_and_uses_dynamic_trip_context_card():
    script = script_text()
    assert "renderTripNav" in script
    assert "renderTripContextCard" in script
    assert "trip.name" in script and "trip.city" in script
    assert "← All trips" in script

    planning_items = ["Itinerary", "Flights", "Suggestions", "FlockMode"]
    active_items = ["Today", "On the trip", "FlockMode", "Expenses", "Alerts"]
    past_items = ["Wrapped"]
    for label in planning_items + active_items + past_items:
        assert label in script

    assert "trip.state === 'planning'" in script
    assert "trip.state === 'active'" in script
    assert "trip.state === 'past'" in script


def test_mobile_drawer_css_and_stateful_controls_exist():
    html = html_text()
    css = style_text()
    script = script_text()

    for marker in [
        ".mobile-topbar",
        ".mobile-menu-button",
        ".sidebar.open",
        ".mobile-backdrop",
        ".mobile-backdrop.show",
        "@media (max-width: 900px)",
        "transform: translateX(-100%)",
        "width: 280px",
    ]:
        assert marker in css

    for marker in [
        "isDrawerOpen",
        "toggleMobileDrawer",
        "closeMobileDrawer",
        "renderMobileTopbar",
        "mobile-menu-button",
        "mobile-backdrop",
        "aria-label=\"Open navigation\"",
    ]:
        assert marker in script or marker in html


def test_nav_clicks_close_mobile_drawer_and_exit_trip_context():
    script = script_text()
    assert "function navigate(" in script
    assert "closeMobileDrawer();" in script
    assert "setTripContext(null)" in script
    assert "state.tripId = null" in script


def test_bv5_contract_marks_app_shell_done():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-005 — Implement v5 app shell, navigation, and mobile drawer**" in contract
    assert "Mobile top bar, drawer, and backdrop are stateful" in contract
