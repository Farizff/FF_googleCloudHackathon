from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "agent" / "system_prompt.txt"
CONFIG = ROOT / "agent" / "agent_config.yaml"

EXPECTED_TOOLS = [
    "get_traveller_profile",
    "search_venues",
    "search_accommodation",
    "get_transit_time",
    "optimise_route",
    "get_weather",
    "search_flights",
    "score_flight_risk",
    "get_multi_modal_transport",
    "apply_disruption",
    "save_itinerary",
    "get_visa_requirements",
    "notify_contacts",
    "poll_flight_status",
]


def test_system_prompt_file_contains_bounce_persona_and_hard_rules():
    prompt = PROMPT.read_text(encoding="utf-8")

    assert prompt.startswith("You are Bounce, an AI group travel companion.")
    assert "Never request passport numbers, payment card details, or national IDs" in prompt
    assert "After apply_disruption, always call notify_contacts" in prompt
    assert "Always present exactly 3 options" in prompt
    assert "Never fabricate" in prompt
    assert "For chat responses, return plain conversational text" in prompt


def test_agent_config_registers_fixed_prd_tool_set():
    config = CONFIG.read_text(encoding="utf-8")

    assert "name: bounce" in config
    assert "system_prompt: agent/system_prompt.txt" in config
    assert "tool_count: 14" in config

    for tool_name in EXPECTED_TOOLS:
        assert f"name: {tool_name}" in config


def test_agent_config_marks_all_fixed_prd_tools_as_implemented():
    config = CONFIG.read_text(encoding="utf-8")

    assert "status: planned" not in config
    assert config.count("status: implemented") == 14
