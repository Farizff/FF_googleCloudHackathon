import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"


def read_frontend(name):
    return (FRONTEND / name).read_text(encoding="utf-8")


def test_bnc032_interaction_contract_exists_and_names_all_new_cards():
    contract = (ROOT / "docs" / "design" / "frontend_interaction_contract.md").read_text(encoding="utf-8")
    kanban = (ROOT / "docs" / "kanban" / "frontend_usability_kanban.md").read_text(encoding="utf-8")

    assert "demo-usable MVP" in contract
    for card_id in range(32, 41):
        assert f"BNC-{card_id:03d}" in kanban

    for control in [
        "#start-button",
        "#send-trip-prompt",
        ".sug-accept",
        ".sug-modify",
        ".sug-decline",
        "#start-flockmode",
        ".ask-bounce-button",
        "#log-expense",
        "#health-button",
        "#seed-button",
        "#disruption-button",
    ]:
        assert control in contract


def test_frontend_javascript_syntax_is_valid():
    result = subprocess.run(
        ["node", "--check", str(FRONTEND / "app.js")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_visible_buttons_have_intentional_behavior_paths():
    html = read_frontend("index.html")
    app_js = read_frontend("app.js")

    button_labels = [re.sub(r"<.*?>", "", label).strip() for label in re.findall(r"<button\b[^>]*>(.*?)</button>", html, re.S)]
    assert button_labels, "frontend should expose visible buttons"

    expected_behavior_markers = [
        "startButton?.addEventListener",
        "sendTripPromptButton?.addEventListener",
        "wirePlanningChips",
        "wireProfileChips",
        "wireSuggestionButtons",
        "wireSplitBillControls",
        "splitIntoFlocksButton?.addEventListener",
        "startFlockModeButton?.addEventListener",
        "logExpenseButton?.addEventListener",
        "ask-bounce-button",
        "healthButton?.addEventListener",
        "seedButton?.addEventListener",
        "disruptionButton?.addEventListener",
        "wireBottomNav",
    ]
    for marker in expected_behavior_markers:
        assert marker in app_js

    inert_labels = {
        "Culture",
        "Food",
        "Shopping",
        "International",
        "Halal-friendly",
        "Art",
        "Low walking first day",
        "Accept",
        "Modify",
        "Decline",
        "Ask Bounce anything about today →",
        "Everyone",
        "Specific people",
        "My Flock",
        "Just me",
        "🍜 Food",
        "🚇 Transport",
        "🎟 Activity",
    }
    missing = [label for label in inert_labels if label not in button_labels]
    assert not missing


def test_frontend_usability_styles_show_selected_and_stateful_controls():
    css = read_frontend("style.css")
    for selector in [
        ".quick-chip.is-selected",
        ".flight-option-card.is-selected",
        ".suggestion-item[data-status=\"accepted\"]",
        ".suggestion-item[data-status=\"declined\"]",
        ".map-canvas::after",
    ]:
        assert selector in css


def test_friend_feature_demo_path_has_visible_backend_backed_controls():
    html = read_frontend("index.html")
    app_js = read_frontend("app.js")

    for expected in [
        'id="join-trip-button"',
        'id="load-itinerary-button"',
        'id="add-flock-btn"',
        'id="save-flockmode-btn"',
        'id="refresh-settlement-button"',
    ]:
        assert expected in html

    for marker in [
        "seedDemoTrip",
        "window.currentTripId = result.trip_id",
        "els.inviteToken.value = result.invite_token",
        "window.currentItineraryId = result.itinerary_id",
        "loadItineraryButton?.addEventListener",
        "refreshSettlementButton?.addEventListener",
        "requestJson('/expenses'",
        "showSettlementView()",
        "flock_name:",
        "leader_user_id:",
        "member_ids:",
        "flight.risk ?? flight.risk_score",
    ]:
        assert marker in app_js

    assert "flocks: flocks" not in app_js
