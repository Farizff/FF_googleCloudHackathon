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


def test_wrap_data_has_unique_details_for_all_three_past_trips():
    script = script_text()
    for marker in [
        "WRAP_DATA",
        "cdmx-reunion",
        "seoul-food-crawl",
        "lisbon-long-weekend",
        "MX$37,000",
        "₩5,900,000",
        "€1,160",
        "MX$9,250/person",
        "₩983,000/person",
        "€290/person",
    ]:
        assert marker in script


def test_wrap_screens_render_total_per_person_categories_settlements_and_bouncesay():
    script = script_text()
    css = style_text()
    for marker in [
        "renderWrapScreen",
        "wrap-summary-grid",
        "wrap-category-grid",
        "wrap-settlement-list",
        "BounceSay insight",
        "categoryBreakdown",
        "settlements",
        "perPerson",
        "total",
    ]:
        assert marker in script or marker in css


def test_destination_local_currency_only_and_no_usd_conversion_or_travel_dna():
    script = script_text()
    wrap_section = script[script.index("function renderWrapScreen"):]
    for local_currency in ["MX$", "₩", "€"]:
        assert local_currency in script
    forbidden = ["USD", "US$", "Travel DNA", "travel dna"]
    for marker in forbidden:
        assert marker not in wrap_section


def test_each_past_trip_has_unique_category_breakdown_and_settlements():
    script = script_text()
    for marker in [
        "Tacos + markets",
        "Metro + rideshare",
        "K-BBQ + markets",
        "Subway passes",
        "Pastéis + seafood",
        "Tram + train",
        "Alex pays Maya",
        "Sofia pays Priya",
        "Jake pays Emma",
    ]:
        assert marker in script


def test_wrap_phase_routes_to_wrap_screen_before_generic_trip_screen():
    script = script_text()
    assert "if (state.phase === 'wrap') { app.innerHTML = renderWrapScreen(); return; }" in script
    assert script.index("if (state.phase === 'wrap')") < script.index("if (state.tripId)")


def test_bv5_contract_marks_wrap_done():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-011 — Build Post-trip Wrap screens**" in contract
    assert "Each past trip renders unique total, per-person amount, category breakdown, settlements, and BounceSay insight" in contract
