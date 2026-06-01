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


def test_profile_screen_has_v5_tabs_and_anchored_editable_save_buttons():
    script = script_text()
    css = style_text()

    for marker in [
        "PROFILE_TABS",
        "about-me",
        "food-diet",
        "how-i-travel",
        "past-trips",
        "passport-visas",
        "About me",
        "Food & diet",
        "How I travel",
        "Past trips",
        "Passport & visas",
        "function renderProfileScreen()",
        "profile-tabs",
        "profile-tab-panel",
        "profile-save-row",
        "Save changes",
    ]:
        assert marker in script or marker in css

    for selector in [
        ".profile-layout",
        ".profile-tabs",
        ".profile-tab",
        ".profile-tab.active",
        ".profile-tab-panel",
        ".profile-save-row",
        ".profile-save-row.is-anchored",
        ".profile-feedback",
    ]:
        assert selector in css


def test_past_trips_tab_is_read_only_without_save_button():
    script = script_text()
    assert "readOnly: true" in script
    assert "Past trips tab is read-only" in script
    assert "!tab.readOnly" in script
    assert "Save changes" in script


def test_profile_save_action_produces_visible_demo_feedback():
    script = script_text()
    for marker in [
        "profileFeedback",
        "saveProfileTab",
        "Saved ${tab.label} changes for the demo",
        "profile-feedback",
        "aria-live=\"polite\"",
    ]:
        assert marker in script


def test_profile_nav_phase_renders_profile_screen():
    script = script_text()
    assert "onclick=\"setPhase('profile')\"" in script
    assert "if (state.phase === 'profile') { app.innerHTML = renderProfileScreen(); return; }" in script
    assert script.index("if (state.phase === 'profile')") < script.index("if (state.tripId)")


def test_bv5_contract_marks_profile_done():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-008 — Build Profile tabs with anchored save buttons**" in contract
    assert "Profile has tabs for About me, Food & diet, How I travel, Past trips, and Passport & visas" in contract
