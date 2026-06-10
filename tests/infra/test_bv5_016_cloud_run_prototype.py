import json
import re
import runpy

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOY_DIR = ROOT / "cloudrun" / "bounce-v5-prototype"


def test_bv5_016_cloud_run_source_serves_v5_prototype_and_health():
    dockerfile = (DEPLOY_DIR / "Dockerfile").read_text(encoding="utf-8")
    app_py = (DEPLOY_DIR / "app.py").read_text(encoding="utf-8")
    index_html = (DEPLOY_DIR / "index.html").read_text(encoding="utf-8")
    prototype_html = (ROOT / "frontend" / "bounce_v5_prototype.html").read_text(encoding="utf-8")

    assert "bounce-v5-prototype" in dockerfile
    assert "EXPOSE 8080" in dockerfile
    assert "--host 0.0.0.0" not in dockerfile  # stdlib server binds in app.py
    assert "0.0.0.0" in app_py
    assert "PORT" in app_py
    assert '"status": "ok"' in app_py
    assert '"service": "bounce-v5-prototype"' in app_py
    assert "Cache-Control" in app_py
    assert "GOOGLE_MAPS_API_KEY" in app_py
    assert "__GOOGLE_MAPS_API_KEY__" in app_py
    assert index_html == prototype_html
    # The adopted React build is a self-contained bundler artifact. Google Maps
    # is loaded from decoded application source and receives its browser-visible
    # key through Cloud Run's runtime template injection, never from a committed
    # raw key.
    assert "__bundler/manifest" in index_html
    assert "google-maps-api-key" in index_html
    assert "AIza" not in index_html  # no real Maps key may leak into the public file


def test_bv5_016_cloud_run_injects_google_maps_key_into_bundled_template(monkeypatch):
    app = runpy.run_path(str(DEPLOY_DIR / "app.py"))
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "TEST_MAPS_KEY")

    rendered = app["render_index_html"]().decode("utf-8")
    template = json.loads(re.search(r'<script type="__bundler/template">(.*?)</script>', rendered, re.S).group(1))

    assert 'meta name="google-maps-api-key" content="TEST_MAPS_KEY"' in template
    assert 'content="__GOOGLE_MAPS_API_KEY__"' not in template


def test_bv5_016_contract_records_option_2_deployment_target():
    contract = (ROOT / "docs" / "kanban" / "bounce_v5_contract.md").read_text(encoding="utf-8")

    assert "BV5-016" in contract
    assert "Option 2" in contract
    assert "bounce-v5-prototype" in contract
    assert "project-411e0419-48bd-4b5b-97f" in contract
    assert "asia-southeast1" in contract
