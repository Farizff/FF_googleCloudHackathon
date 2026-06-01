from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "qa" / "bv5_015_visual_responsive_smoke.md"
CONTRACT = ROOT / "docs" / "kanban" / "bounce_v5_contract.md"


def report_text():
    assert REPORT.exists(), "BV5-015 should leave committed local visual/responsive smoke evidence"
    return REPORT.read_text(encoding="utf-8")


def test_smoke_report_records_required_viewports_and_console_status():
    report = report_text()
    for marker in [
        "1280x900 desktop",
        "1024x768 tablet",
        "360x800 mobile",
        "Browser console startup errors: none",
        "Playwright Chromium",
    ]:
        assert marker in report


def test_smoke_report_records_layout_acceptance_evidence():
    report = report_text()
    for marker in [
        "desktop: app shell and full layout rendered",
        "tablet: itinerary/right-rail layout rendered",
        "mobile: drawer opens/closes and stacked layout rendered down to 360px",
        "representative demo path completed end to end",
    ]:
        assert marker in report


def test_bv5_contract_marks_visual_smoke_done_with_deployment_checkpoint_preserved():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-015 — Local visual/responsive smoke pass**" in contract
    assert "docs/qa/bv5_015_visual_responsive_smoke.md" in contract
    assert "- **BV5-016 — Decide and perform deployment path**" in contract
    assert "Recommended next action: **BV5-017 — Reconcile L2 backend contract to v5**" in contract
