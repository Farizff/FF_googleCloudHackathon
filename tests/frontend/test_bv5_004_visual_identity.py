import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOTYPE = ROOT / "frontend" / "bounce_v5_prototype.html"
CONTRACT = ROOT / "docs" / "kanban" / "bounce_v5_contract.md"


def html_text():
    return PROTOTYPE.read_text(encoding="utf-8")


def style_text():
    html = html_text()
    match = re.search(r"<style>(.*?)</style>", html, re.S)
    assert match, "prototype should keep all CSS inline in one style block"
    return match.group(1)


def root_block():
    css = style_text()
    match = re.search(r":root\s*\{(?P<body>.*?)\n\s*\}", css, re.S)
    assert match, "prototype should declare a :root token block"
    return match.group("body")


def css_without_root():
    css = style_text()
    return re.sub(r":root\s*\{.*?\n\s*\}", "", css, count=1, flags=re.S)


def test_bv5_full_token_block_matches_design_system_names_and_key_values():
    root = root_block()
    expected_tokens = {
        "--purple": "#1A0A6B",
        "--purple-mid": "#4A2FC4",
        "--purple-light": "#6B50E8",
        "--purple-tint": "#EDE9FF",
        "--lime": "#C8E64A",
        "--lime-dark": "#8DC63F",
        "--lime-tint": "#F0FFD4",
        "--lime-text": "#3A5200",
        "--orange": "#F47B20",
        "--orange-yellow": "#FBBF24",
        "--success": "#16A34A",
        "--warning": "#D97706",
        "--danger": "#DC2626",
        "--cat-food": "#F47B20",
        "--cat-culture": "#7C3AED",
        "--cat-nature": "#16A34A",
        "--cat-transport": "#1A0A6B",
        "--bg-page": "#FAF8FF",
        "--text-secondary": "#5B5F6E",
        "--font-logo": "'Baloo 2'",
        "--font-display": "'Nunito'",
        "--text-3xl": "48px",
        "--r-2xl": "30px",
        "--z-judge": "500",
    }
    for token, value in expected_tokens.items():
        assert token in root, f"missing v5 token {token}"
        assert value in root, f"{token} should keep design-system value {value}"

    for old_token in ["--yale", "--lemon", "--teal", "--amber"]:
        assert old_token not in root


def test_bv5_component_css_uses_tokens_instead_of_raw_hex_outside_root():
    component_css = css_without_root()
    raw_hexes = re.findall(r"#[0-9A-Fa-f]{3,8}", component_css)
    assert raw_hexes == [], f"component CSS should use var() tokens, found raw hex values: {raw_hexes}"

    for required_var in [
        "var(--purple)",
        "var(--purple-mid)",
        "var(--purple-tint)",
        "var(--lime)",
        "var(--lime-text)",
        "var(--orange-tint)",
        "var(--bg-card)",
        "var(--text-secondary)",
        "var(--shadow-card)",
        "var(--shadow-float)",
    ]:
        assert required_var in component_css


def test_bv5_visual_identity_components_exist_in_prototype_markup_and_css():
    html = html_text()
    css = style_text()
    for selector in [
        ".logomark",
        ".bounce-avatar",
        ".bounce-avatar-sm",
        ".bounce-fab",
        ".bounce-fab.has-alert::before",
        ".tag-lime",
        ".tag-purple",
        ".tag-orange",
        ".card-purple",
        ".btn",
        ".btn-primary",
        ".btn-lime",
        ".btn-ghost",
        "@keyframes pulse-ring",
    ]:
        assert selector in css, f"missing visual identity selector {selector}"

    for marker in [
        'class="logomark"',
        'aria-label="Bounce"',
        'class="bounce-avatar bounce-avatar-sm"',
        'class="bounce-fab has-alert"',
        'aria-label="Chat with Bounce"',
    ]:
        assert marker in html, f"missing prototype markup marker {marker}"


def test_bv5_contract_marks_visual_identity_done():
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "### DONE" in contract
    assert "- **BV5-004 — Apply v5 visual identity and design tokens**" in contract
    assert "Bounce logomark fallback, Bounce avatar, FAB alert state, cards, tags, and button variants exist" in contract
