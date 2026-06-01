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


def test_active_today_uses_tokyo_day_3_data_and_quick_actions():
    script = script_text()
    css = style_text()
    for marker in [
        "ACTIVE_TODAY",
        "Tokyo Day 3",
        "renderActiveTodayScreen",
        "Shibuya crossing coffee check-in",
        "TeamLab Borderless window",
        "Quick actions",
        "Ping late group",
        "sendLateGroupPing",
        "Ping drafted: Meet at Hachikō in 10 minutes.",
        "activeActionFeedback",
        "Open FlockMode",
        "Trigger disruption",
        "active-today-grid",
        "quick-action-grid",
    ]:
        assert marker in script or marker in css


def test_flockmode_switcher_schedule_countdown_google_map_and_photo_placeholder():
    script = script_text()
    css = style_text()
    for marker in [
        "FLOCKS",
        "renderActiveFlockScreen",
        "setActiveFlock",
        "active flock schedule",
        "Meet at Shibuya Hachikō",
        "countdown-chip",
        "18 min until meetup",
        "flock-google-map",
        "Real Google map · Tokyo FlockMode",
        "Photo sharing placeholder",
    ]:
        assert marker in script or marker in css


def test_disruption_modal_has_three_alternatives_and_required_copy():
    script = script_text()
    for marker in [
        "DISRUPTION_OPTIONS",
        "renderDisruptionModal",
        "openDisruptionModal",
        "Shinjuku food hall pivot",
        "Harajuku indoor arcade",
        "Hotel reset + later ramen",
        "Lock this in & ping everyone →",
        "Not now",
    ]:
        assert marker in script
    assert script.count("impact:") >= 3


def test_expenses_include_four_split_modes_six_categories_and_local_updates():
    script = script_text()
    css = style_text()
    for marker in [
        "SPLIT_MODES",
        "Equally",
        "By item",
        "By percentage",
        "Custom shares",
        "EXPENSE_CATEGORIES",
        "Food",
        "Culture",
        "Transport",
        "Shopping",
        "Hotel",
        "Wellness",
        "setExpenseSplitMode",
        "setExpenseCategory",
        "Expense split updated locally",
        "renderActiveExpensesScreen",
    ]:
        assert marker in script or marker in css
    assert script.count("category:") >= 6


def test_alerts_have_populated_and_empty_states():
    script = script_text()
    for marker in [
        "ALERTS",
        "renderActiveAlertsScreen",
        "Rain starts near Shinjuku at 17:30",
        "JR Yamanote crowding is high",
        "No alerts for this view",
        "showEmptyAlerts",
        "toggleEmptyAlerts",
    ]:
        assert marker in script


def test_active_phases_route_to_specific_screens_before_generic_trip_screen():
    script = script_text()
    for marker in [
        "if (state.phase === 'active-today') { app.innerHTML = renderActiveTodayScreen(); return; }",
        "if (state.phase === 'active-flock') { app.innerHTML = renderActiveFlockScreen(); return; }",
        "if (state.phase === 'active-expenses') { app.innerHTML = renderActiveExpensesScreen(); return; }",
        "if (state.phase === 'active-alerts') { app.innerHTML = renderActiveAlertsScreen(); return; }",
    ]:
        assert marker in script
    assert script.index("if (state.phase === 'active-today')") < script.index("if (state.tripId)")


def test_bv5_contract_marks_active_done():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-010 — Build Active Today, FlockMode, disruption, expenses, and alerts**" in contract
    assert "Today screen uses Tokyo Day 3 data and quick actions" in contract
