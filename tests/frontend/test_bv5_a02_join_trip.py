import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOTYPE = ROOT / "frontend" / "bounce_v5_prototype.html"
CLOUDRUN_COPY = ROOT / "cloudrun" / "bounce-v5-prototype" / "index.html"
CONTRACT = ROOT / "docs" / "kanban" / "bounce_v5_contract.md"


def html_text(path=PROTOTYPE):
    return path.read_text(encoding="utf-8")


def script_text(path=PROTOTYPE):
    match = re.search(r"<script>(.*?)</script>", html_text(path), re.S)
    assert match, "prototype should keep JavaScript inline"
    return match.group(1)


def test_join_nav_renders_deterministic_l1_join_screen():
    script = script_text()

    for marker in [
        "function renderJoinScreen",
        "Join a trip",
        "Enter invite code",
        "L1 invite preview",
        "Join preview loaded for the demo",
        "Join Maya's 30th preview",
        "Backend join flow stays deferred in L1",
    ]:
        assert marker in script

    assert "if (state.phase === 'join') { app.innerHTML = renderJoinScreen(); return; }" in script
    assert "onclick=\"previewJoinCode()\"" in script
    assert "join-code-input" in script


def test_cloudrun_copy_contains_same_join_screen_contract():
    script = script_text(CLOUDRUN_COPY)

    assert "function renderJoinScreen" in script
    assert "Join preview loaded for the demo" in script
    assert "if (state.phase === 'join') { app.innerHTML = renderJoinScreen(); return; }" in script


def test_bv5_a02_addendum_is_recorded_done_with_durable_evidence():
    contract = CONTRACT.read_text(encoding="utf-8")

    assert "## Approved v5 polish addendum" in contract
    assert "- **BV5-A02 — Fix global Join a trip nav**" in contract
    assert "Status: DONE" in contract
    assert "tests/frontend/test_bv5_a02_join_trip.py" in contract
    assert "Global `Join a trip` nav opens a deterministic V5 L1 Join screen." in contract
