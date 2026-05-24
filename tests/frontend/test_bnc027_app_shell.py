import json
from html.parser import HTMLParser
from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


class TagCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def parse_index():
    parser = TagCollector()
    parser.feed((FRONTEND / "index.html").read_text(encoding="utf-8"))
    return parser.tags


def test_frontend_foundation_files_exist_and_index_wires_assets():
    expected = ["index.html", "manifest.json", "sw.js", "app.js", "style.css"]
    for name in expected:
        assert (FRONTEND / name).exists(), f"missing frontend/{name}"

    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    tags = parse_index()

    assert '<main id="app"' in html
    assert '<link rel="manifest" href="manifest.json"' in html
    assert any(tag == "link" and attrs.get("href") == "style.css" for tag, attrs in tags)
    assert any(tag == "script" and attrs.get("src") == "app.js" and attrs.get("defer") is not None for tag, attrs in tags)
    assert "navigator.serviceWorker.register('sw.js')" in html


def test_manifest_is_installable_pwa_shell():
    manifest = json.loads((FRONTEND / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["name"] == "Bounce"
    assert manifest["short_name"] == "Bounce"
    assert manifest["start_url"] == "."
    assert manifest["display"] == "standalone"
    assert manifest["theme_color"] == "#0D3B66"
    assert manifest["background_color"] == "#F7F7F2"
    assert {icon["sizes"] for icon in manifest["icons"]} >= {"192x192", "512x512"}


def test_app_js_can_call_backend_health_and_judge_demo_endpoints():
    app_js = (FRONTEND / "app.js").read_text(encoding="utf-8")

    assert "const API_BASE" in app_js
    assert "async function checkHealth" in app_js
    assert "fetch(`${API_BASE}/health`)" in app_js
    assert "async function seedDemoTrip" in app_js
    assert "fetch(`${API_BASE}/judge/seed-demo-trip`, { method: 'POST' })" in app_js
    assert "async function triggerDisruption" in app_js
    assert "fetch(`${API_BASE}/judge/trigger-disruption`, { method: 'POST' })" in app_js


def test_style_uses_design_tokens_and_auth_shell_components():
    css = (FRONTEND / "style.css").read_text(encoding="utf-8")

    assert "--yale:           #0D3B66;" in css
    assert "--lemon:          #FAF0CA;" in css
    assert ".auth-screen" in css
    assert ".bounce-avatar" in css
    assert ".bottom-nav" in css
    assert ".api-status" in css


def test_service_worker_caches_app_shell_files_only():
    sw = (FRONTEND / "sw.js").read_text(encoding="utf-8")

    assert "bounce-app-shell" in sw
    for asset in ["./", "./index.html", "./style.css", "./app.js", "./manifest.json"]:
        assert asset in sw
    assert "self.addEventListener('install'" in sw
    assert "self.addEventListener('fetch'" in sw
