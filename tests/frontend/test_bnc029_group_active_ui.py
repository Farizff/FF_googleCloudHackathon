from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def read_frontend(name):
    return (FRONTEND / name).read_text(encoding="utf-8")


def test_bnc029_group_flock_active_and_split_bill_sections_exist():
    html = read_frontend("index.html")

    required_sections = [
        'id="group-dashboard"',
        'id="suggestion-review"',
        'id="flockmode-creation"',
        'id="flock-active-view"',
        'id="active-trip-view"',
        'id="split-bill"',
    ]
    for marker in required_sections:
        assert marker in html

    assert 'data-phase="active"' in html
    assert 'Group dashboard' in html
    assert 'Suggestion review' in html
    assert 'Create Flocks for Day 5' in html
    assert 'Start FlockMode' in html
    assert 'Ask Bounce anything about today' in html
    assert 'Log expense' in html


def test_bnc029_ui_contains_required_demo_content_and_controls():
    html = read_frontend("index.html")

    required_copy = [
        '7 joined',
        '3 pending',
        'Split into Flocks',
        'The Explorers',
        'Shinjuku Station East Exit',
        'NH106 SFO → NRT',
        'NOW',
        'teamLab Borderless',
        'Everyone',
        'Specific people',
        'My Flock',
        'Just me',
        'Split between: Alex, Priya, Carlos',
    ]
    for copy in required_copy:
        assert copy in html


def test_bnc029_app_js_renders_group_dashboard_flockmode_and_split_bill_state():
    app_js = read_frontend("app.js")

    for function_name in [
        "demoActiveTripSnapshot",
        "renderGroupDashboard",
        "renderSuggestionReview",
        "renderFlockMode",
        "renderActiveTrip",
        "renderSplitBill",
        "activateFlockMode",
        "logDemoExpense",
    ]:
        assert f"function {function_name}" in app_js

    assert "group-dashboard" in app_js
    assert "flock-active-view" in app_js
    assert "split-bill" in app_js
    assert "dataset.phase = 'active'" in app_js


def test_bnc029_styles_cover_group_flock_active_trip_and_split_bill_surfaces():
    css = read_frontend("style.css")

    for selector in [
        ".group-dashboard-card",
        ".member-status-grid",
        ".suggestion-panel",
        ".suggestion-count-badge",
        ".flock-dropzone",
        ".flock-active-card",
        ".reconvene-countdown",
        ".active-trip-card",
        ".now-badge",
        ".expense-tabs",
        ".amount-input",
        ".balance-grid",
        ".balance-card",
    ]:
        assert selector in css
