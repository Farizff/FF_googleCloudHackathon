import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"
PROTOTYPE = FRONTEND / "bounce_v5_prototype.html"
CONTRACT = ROOT / "docs" / "kanban" / "bounce_v5_contract.md"


class TagCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def prototype_text():
    return PROTOTYPE.read_text(encoding="utf-8")


def parsed_tags():
    parser = TagCollector()
    parser.feed(prototype_text())
    return parser.tags


def test_bv5_l1_prototype_file_exists_and_is_single_html_shell():
    assert PROTOTYPE.exists(), "BV5-003 should create frontend/bounce_v5_prototype.html"

    html = prototype_text()
    assert "<!doctype html>" in html.lower()
    assert '<main id="app"' in html
    assert "Bounce v5 L1 prototype" in html
    assert "<style>" in html and "</style>" in html
    assert "<script>" in html and "</script>" in html

    tags = parsed_tags()
    external_assets = [
        (tag, attrs)
        for tag, attrs in tags
        if attrs.get("src")
        or (tag == "link" and attrs.get("href") and attrs.get("rel") != "canonical")
    ]
    assert external_assets == [], f"L1 shell must be self-contained; found {external_assets}"


def test_bv5_l1_prototype_uses_const_demo_data_near_top_without_browser_storage_or_fetch():
    html = prototype_text()
    lower = html.lower()

    script_match = re.search(r"<script>(.*?)</script>", html, re.S)
    assert script_match, "prototype should use one inline script"
    script = script_match.group(1)
    first_1200 = script[:1200]

    assert "const DEMO_TRIPS" in first_1200
    assert "const WRAP_DATA" in script
    for required_trip in ["lisbon_planning", "tokyo_active", "seoul_past", "bali_past", "melbourne_past"]:
        assert required_trip in script

    banned = ["localStorage", "sessionStorage", "indexedDB", "fetch(", "XMLHttpRequest", "navigator.sendBeacon"]
    for token in banned:
        assert token.lower() not in lower, f"BV5 L1 prototype should not use {token}"


def test_bv5_l1_prototype_declares_required_v5_routes_and_cut_boundaries():
    html = prototype_text()
    script = re.search(r"<script>(.*?)</script>", html, re.S).group(1)

    for route in ["/", "/trip/:id", "/trip/:id/plan", "/trip/:id/active", "/trip/:id/flock", "/trip/:id/wrap", "/chat", "/join/:token"]:
        assert route in script

    for removed_route in ["/compliance", "/waiting", "/predeparture"]:
        assert removed_route not in html

    for cut_marker in ["Photo sharing coming soon", "Multi-city trips are future scope", "Travel DNA is removed"]:
        assert cut_marker in html


def test_bv5_l1_prototype_has_minimal_render_and_role_state_hooks():
    html = prototype_text()
    script = re.search(r"<script>(.*?)</script>", html, re.S).group(1)

    for marker in [
        "function renderApp()",
        "function renderHomeScreen()",
        "function setTripContext(",
        "function setRole(",
        "function setPhase(",
        "const state =",
        "role: 'organiser'",
        "phase: 'home'",
    ]:
        assert marker in script

    for copy in [
        "Plan trips together, without the chaos.",
        "Your trip starts here. Tell me what you've got in mind.",
        "⚡ Demo controls · drag me",
    ]:
        assert copy in html


def test_bv5_contract_marks_card_done_and_preserves_fixed_kanban():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-003 — Create the v5 L1 prototype shell**" in contract
    assert "Prototype loads as one self-contained HTML file" in contract
    assert "### TODO" in contract
