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


def test_bounce_fab_matches_mascot_ring_pulse_and_opens_panel():
    script = script_text()
    css = style_text()
    for marker in [
        "bounce-fab",
        "has-alert",
        "pulse-ring",
        "openBounceAssistant",
        "closeBounceAssistant",
        "isBounceOpen",
        "aria-label=\"Open Bounce assistant\"",
    ]:
        assert marker in script or marker in css
    assert "border: 3px solid var(--lime)" in css
    assert "box-shadow: var(--shadow-bounce)" in css


def test_chat_panel_has_dialog_aria_header_stream_pill_input_and_close():
    script = script_text()
    css = style_text()
    for marker in [
        "renderBounceAssistantPanel",
        "role=\"dialog\"",
        "aria-modal=\"false\"",
        "aria-label=\"Bounce assistant\"",
        "bounce-chat-panel",
        "bounce-chat-header",
        "bounce-message-stream",
        "bounce-pill-input",
        "Close Bounce assistant",
    ]:
        assert marker in script or marker in css


def test_permission_label_changes_for_roles():
    script = script_text()
    for marker in [
        "permissionLabelForRole",
        "Organiser/Co-leader can edit plans, budgets, and alerts.",
        "Flock leader can guide meetups and disruption pivots.",
        "Member can suggest ideas and view group decisions.",
        "state.role === 'co-leader'",
        "state.role === 'flock-leader'",
        "state.role === 'member'",
    ]:
        assert marker in script


def test_l1_bounce_responses_are_deterministic_and_do_not_fetch():
    script = script_text()
    for marker in [
        "BOUNCE_RESPONSES",
        "deterministicBounceResponse",
        "sendBounceMessage",
        "I can help with the current demo screen using local prototype data.",
        "For this L1 prototype, I’ll keep the answer deterministic and offline.",
    ]:
        assert marker in script
    assert "fetch(" not in script
    assert "EventSource" not in script
    assert "XMLHttpRequest" not in script


def test_chat_phase_and_fab_route_render_assistant_panel():
    script = script_text()
    assert "if (state.phase === 'chat') { app.innerHTML = renderChatScreen(); return; }" in script
    assert "renderChatScreen" in script
    assert "renderBounceAssistantPanel()" in script


def test_bv5_contract_marks_assistant_done_with_durable_evidence():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-012 — Build Bounce assistant panel, FAB, and role labels**" in contract
    assert "tests/frontend/test_bv5_012_bounce_assistant.py" in contract
    assert "L1 responses are deterministic and do not fetch." in contract
