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


def test_plan_entry_response_detects_prompt_destination_markers():
    script = script_text()

    for marker in [
        "function destinationFromPrompt",
        "const PROMPT_DESTINATION_RESPONSES",
        "tokyo",
        "Tokyo",
        "lisbon",
        "Lisbon",
        "seoul",
        "Seoul",
        "state.entryPrompt",
        "destinationFromPrompt(state.entryPrompt)",
    ]:
        assert marker in script

    assert "For Lisbon, I’d start" in script
    assert "For Tokyo, I’d start" in script
    assert "For Seoul, I’d start" in script


def test_cloudrun_copy_has_same_prompt_destination_contract():
    script = script_text(CLOUDRUN_COPY)

    assert "function destinationFromPrompt" in script
    assert "destinationFromPrompt(state.entryPrompt)" in script
    assert "For Tokyo, I’d start" in script


def test_bv5_a03_addendum_is_done_and_pointer_advances():
    contract = CONTRACT.read_text(encoding="utf-8")

    assert "- **BV5-A03 — Make Plan-new-trip response reflect typed prompt**" in contract
    assert "Status: DONE" in contract
    assert "tests/frontend/test_bv5_a03_prompt_destination.py" in contract
    assert "Recommended next action: **BV5-A04 — Add disruption locked and pinged confirmation**" in contract
