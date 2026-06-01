import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOTYPE = ROOT / "frontend" / "bounce_v5_prototype.html"
CONTRACT = ROOT / "docs" / "kanban" / "bounce_v5_contract.md"


def html_text():
    return PROTOTYPE.read_text(encoding="utf-8")


def script_text():
    match = re.search(r"<script>(.*?)</script>", html_text(), re.S)
    assert match, "prototype should keep its JavaScript inline"
    return match.group(1)


def test_required_v5_copy_routes_hash_states_nav_and_cut_placeholders():
    html = html_text()
    script = script_text()
    for marker in [
        "Prototype hash route shape: screen=X&phase=Y&user=Z",
        "ROUTES = ['/', '/trip/:id', '/trip/:id/plan', '/trip/:id/active', '/trip/:id/flock', '/trip/:id/wrap', '/chat', '/join/:token']",
        "Home",
        "Plan a new trip",
        "Join a trip",
        "Your trip starts here. Tell me what you've got in mind.",
        "Itinerary",
        "Flights",
        "Suggestions",
        "FlockMode",
        "Expenses",
        "Alerts",
        "Wrapped",
        "Photo sharing placeholder",
        "Multi-city trips are future scope",
        "Travel DNA is removed",
    ]:
        assert marker in html or marker in script


def test_removed_routes_and_cut_features_do_not_exist_as_routes_or_renderers():
    html = html_text()
    script = script_text()
    for removed_route in ["/compliance", "/waiting", "/predeparture"]:
        assert removed_route not in script
    for removed_renderer in [
        "renderCompliance",
        "renderWaiting",
        "renderPredeparture",
        "renderTravelDNA",
        "renderDarkMode",
        "renderNativeApp",
    ]:
        assert removed_renderer not in script
    assert "localStorage" not in script
    assert "sessionStorage" not in script


def test_l1_prototype_has_no_storage_or_network_apis():
    script = script_text()
    banned = [
        "localStorage",
        "sessionStorage",
        "indexedDB",
        "fetch(",
        "XMLHttpRequest",
        "EventSource",
        "navigator.sendBeacon",
        "WebSocket",
    ]
    for marker in banned:
        assert marker not in script


def test_flockmode_photo_sharing_is_placeholder_only():
    script = script_text()
    flock_start = script.index("function renderActiveFlockScreen")
    flock_end = script.index("function renderActiveExpensesScreen")
    flock_renderer = script[flock_start:flock_end]
    assert "Photo sharing placeholder — uploads stay CUT in L1." in flock_renderer
    for forbidden in [
        "type=\"file\"",
        "accept=\"image",
        "uploadPhoto",
        "uploadImage",
        "camera",
        "FileReader",
        "FormData",
        "navigator.mediaDevices",
    ]:
        assert forbidden not in flock_renderer


def test_no_obvious_external_asset_or_script_requests_except_approved_none_for_l1():
    html = html_text()
    external_attrs = re.findall(r"<(?:script|link|img|source|iframe)\b[^>]+(?:src|href)=['\"](https?://|//)[^'\"]+['\"]", html, flags=re.I)
    assert external_attrs == []
    assert "<script src=" not in html
    assert "<link" not in html
    assert "@import" not in html


def test_bv5_contract_marks_automated_checks_done_with_durable_evidence():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-014 — Add v5 prototype automated checks**" in contract
    assert "tests/frontend/test_bv5_014_automated_checks.py" in contract
    assert "Tests verify FlockMode photo sharing remains placeholder-only." in contract
