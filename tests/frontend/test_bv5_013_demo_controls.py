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


def test_demo_controls_panel_starts_bottom_left_above_everything():
    css = style_text()
    script = script_text()
    assert ".judge-panel" in css
    assert "position: fixed" in css
    assert "left: var(--sp-6)" in css
    assert "bottom: var(--sp-6)" in css
    assert "z-index: var(--z-judge)" in css
    assert "--z-judge: 500" in css
    assert "judgePosition" in script


def test_demo_controls_toggle_lime_pill_and_label_are_rendered():
    script = script_text()
    css = style_text()
    for marker in [
        "⚡ Demo controls · drag me",
        "⚡ Demo controls",
        "toggleJudgePanel",
        "isJudgeOpen",
        "judge-panel-pill",
        "aria-expanded",
    ]:
        assert marker in script or marker in css
    assert ".judge-panel-pill" in css
    assert "background: var(--lime)" in css


def test_demo_controls_drag_handlers_update_position():
    script = script_text()
    for marker in [
        "startJudgeDrag",
        "moveJudgeDrag",
        "endJudgeDrag",
        "pointerdown",
        "pointermove",
        "pointerup",
        "setPointerCapture",
        "style=\"left: ${state.judgePosition.x}px; bottom: auto; top: ${state.judgePosition.y}px;\"",
    ]:
        assert marker in script


def test_demo_controls_role_phase_trigger_disruption_and_reset_actions():
    script = script_text()
    for marker in [
        "setRole(this.value)",
        "setDemoPhase(this.value)",
        "triggerDemoDisruption",
        "resetDemoControls",
        "Trigger disruption",
        "Reset demo controls",
        "planning-itinerary",
        "active-today",
        "wrap",
    ]:
        assert marker in script


def test_demo_controls_contract_done_with_durable_evidence():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-013 — Build draggable Judge / Demo Controls panel**" in contract
    assert "tests/frontend/test_bv5_013_demo_controls.py" in contract
    assert "Panel toggles open/collapsed with lime pill `⚡ Demo controls`." in contract
