from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def read_frontend(name):
    return (FRONTEND / name).read_text(encoding="utf-8")


def test_core_planning_sections_exist_in_app_shell():
    html = read_frontend("index.html")

    required_sections = [
        'id="entry-conversation"',
        'id="profile-gap-fill"',
        'id="itinerary-view"',
        'id="budget-tracker"',
        'id="map-preview"',
        'id="flight-selection"',
    ]
    for marker in required_sections:
        assert marker in html

    assert 'id="trip-prompt"' in html
    assert 'id="send-trip-prompt"' in html
    assert 'data-category="Culture"' in html
    assert 'data-mode="International"' in html


def test_core_planning_ui_contains_demo_path_content_and_accessible_regions():
    html = read_frontend("index.html")

    assert 'aria-labelledby="entry-title"' in html
    assert 'Tell me about your trip' in html
    assert 'Quick details' in html
    assert 'Tokyo Reunion' in html
    assert 'Group ready after staggered arrivals' in html
    assert 'Budget tracker' in html
    assert 'Map preview' in html
    assert 'ANA NH106' in html
    assert 'Risk 84/100' in html
    assert 'Budget' in html and 'Recommended' in html and 'Premium' in html


def test_app_js_posts_chat_prompt_and_renders_planning_response():
    app_js = read_frontend("app.js")

    assert "async function sendTripPrompt" in app_js
    assert "fetch(`${API_BASE}/chat`" in app_js
    assert "method: 'POST'" in app_js
    assert "renderPlanningSnapshot" in app_js
    assert "renderFlightOptions" in app_js
    assert "renderBudgetTracker" in app_js
    assert "renderMapPins" in app_js
    assert "trip-prompt" in app_js


def test_core_planning_styles_cover_cards_flights_budget_and_map_pins():
    css = read_frontend("style.css")

    for selector in [
        ".planning-shell",
        ".entry-card",
        ".profile-card",
        ".itinerary-timeline",
        ".budget-meter",
        ".map-pin",
        ".route-line",
        ".flight-option-card",
        ".risk-bar",
        ".quick-chip",
    ]:
        assert selector in css
