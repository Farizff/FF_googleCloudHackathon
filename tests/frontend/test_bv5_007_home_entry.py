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


def test_home_screen_component_tree_matches_v5_design_markers():
    script = script_text()
    css = style_text()

    for marker in [
        "function renderHomeScreen()",
        "home-plan-new",
        "home-plan-new-icon",
        "home-plan-new-body",
        "home-plan-new-title",
        "home-plan-new-sub",
        "home-plan-new-arrow",
        "Plan a new trip",
        "Your trip starts here. Tell me what you've got in mind.",
        "Upcoming trips",
        "On the road right now",
        "Past trips",
    ]:
        assert marker in script or marker in css

    for selector in [
        ".home-plan-new",
        ".home-plan-new-icon",
        ".home-plan-new-title",
        ".home-plan-new-sub",
        ".home-plan-new-arrow",
        ".trip-card",
        ".trip-cover",
        ".trip-state-badge",
        ".trip-meta",
        ".trip-name",
        ".avatar-stack",
    ]:
        assert selector in css


def test_trip_cards_render_cover_badges_days_and_avatar_stack():
    script = script_text()
    for marker in [
        "function renderTripCard(trip)",
        "trip-cover",
        "trip-state-badge",
        "trip-meta",
        "trip-name",
        "avatar-stack",
        "renderAvatarStack(trip)",
        "daysToGo",
        "days to go",
        "tripStateBadge(trip)",
        "Open ${trip.name}",
    ]:
        assert marker in script


def test_entry_conversation_screen_has_textarea_chips_mascot_and_deterministic_response():
    script = script_text()
    css = style_text()

    for marker in [
        "function renderEntryScreen()",
        "entry-conversation",
        "entry-hero",
        "entry-mascot",
        "trip-prompt-textarea",
        "What kind of trip is this?",
        "Birthday trip",
        "Friends reunion",
        "Food crawl",
        "Low walking first day",
        "Beach reset",
        "submitTripPrompt",
        "toggleTripChip",
        "deterministicPlanningResponse",
        "Organising everyone's ideas…",
        "Ready to bounce →",
    ]:
        assert marker in script or marker in css

    for selector in [
        ".entry-conversation",
        ".entry-hero",
        ".entry-mascot",
        ".trip-prompt-textarea",
        ".trip-type-chips",
        ".trip-type-chip.is-selected",
        ".entry-response",
    ]:
        assert selector in css

    assert "fetch(" not in script
    assert "EventSource" not in script


def test_home_plan_cta_and_nav_phase_render_entry_screen():
    script = script_text()
    assert "onclick=\"setPhase('plan')\"" in script
    assert "if (state.phase === 'plan') { app.innerHTML = renderEntryScreen(); return; }" in script
    assert "if (state.phase === 'home') { app.innerHTML = renderHomeScreen(); return; }" in script


def test_bv5_contract_marks_home_entry_done_and_points_to_profile():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-007 — Build Home and Entry Conversation screens**" in contract
    assert "Recommended next action: **BV5-008 — Build Profile tabs with anchored save buttons**" in contract
