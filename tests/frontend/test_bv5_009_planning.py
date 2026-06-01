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


def style_text():
    match = re.search(r"<style>(.*?)</style>", html_text(), re.S)
    assert match, "prototype should keep CSS inline"
    return match.group(1)


def test_planning_itinerary_has_day_rail_toggles_cards_budget_and_map():
    script = script_text()
    css = style_text()

    for marker in [
        "PLANNING_DAYS",
        "renderPlanningItineraryScreen",
        "planning-layout",
        "planning-day-rail",
        "Day 1",
        "Day 2",
        "Day 3",
        "view-toggle",
        "Timeline",
        "Map",
        "activity-card",
        "BudgetCard",
        "planning-map-card",
        "Lisbon map placeholder",
    ]:
        assert marker in script or marker in css

    for selector in [
        ".planning-layout",
        ".planning-day-rail",
        ".planning-main-grid",
        ".view-toggle",
        ".activity-card",
        ".activity-menu",
        ".budget-card",
        ".planning-map-card",
    ]:
        assert selector in css


def test_planning_role_aware_activity_menus_and_member_read_only_copy():
    script = script_text()
    assert "canEditPlanning()" in script
    assert "state.role !== 'member'" in script
    assert "activity-menu" in script
    assert "aria-label=\"Activity options\"" in script
    assert "Members can suggest changes, but organisers edit the plan." in script
    assert "Admin roles can rebalance timing, budget, and options." in script


def test_budget_editor_has_two_inputs_bottom_save_and_feedback():
    script = script_text()
    for marker in [
        "budget-total-input",
        "budget-per-day-input",
        "saveBudgetDraft",
        "Budget saved for the demo",
        "budget-save-row is-anchored",
        "Save budget",
    ]:
        assert marker in script


def test_flights_show_three_options_per_origin_group_with_risk_labels():
    script = script_text()
    for marker in [
        "FLIGHT_GROUPS",
        "London",
        "Singapore",
        "New York",
        "Low risk",
        "Medium risk",
        "Tight connection",
        "flight-option",
        "renderPlanningFlightsScreen",
    ]:
        assert marker in script
    assert script.count("risk:") >= 9


def test_suggestions_have_two_pending_items_and_lime_badge_over_nav_icon():
    script = script_text()
    css = style_text()
    for marker in [
        "SUGGESTIONS",
        "Pastéis de Belém breakfast",
        "Sunset miradouro picnic",
        "status: 'pending'",
        "renderPlanningSuggestionsScreen",
        "suggestions-nav-badge",
    ]:
        assert marker in script or marker in css
    assert script.count("status: 'pending'") == 2
    assert ".suggestions-nav-badge" in css
    assert "position: absolute" in css
    assert "background: var(--lime)" in css


def test_planning_phases_route_to_specific_screens():
    script = script_text()
    assert "if (state.phase === 'planning-itinerary') { app.innerHTML = renderPlanningItineraryScreen(); return; }" in script
    assert "if (state.phase === 'planning-flights') { app.innerHTML = renderPlanningFlightsScreen(); return; }" in script
    assert "if (state.phase === 'planning-suggestions') { app.innerHTML = renderPlanningSuggestionsScreen(); return; }" in script


def test_bv5_contract_marks_planning_done_and_points_to_active_card():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-009 — Build Planning itinerary, budget, map, flights, and suggestions**" in contract
    assert "Recommended next action: **BV5-010 — Build Active Today, FlockMode, disruption, expenses, and alerts**" in contract
