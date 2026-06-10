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
    # The adopted React build is a self-contained bundler artifact: it renders
    # an inline SVG map (no Google Maps), so the served file no longer carries a
    # __GOOGLE_MAPS_API_KEY__ placeholder. app.py's key-injection replace is now
    # a harmless no-op kept for the deployment contract (see kanban adopt-react
    # note). The signature hero copy lives inside base64 assets, not plaintext,
    # so assert the bundler structure instead of greppable copy.
    assert "__bundler/manifest" in index_html
    assert "AIza" not in index_html  # no real Maps key may leak into the public file


def test_bv5_016_contract_records_option_2_deployment_target():
    contract = (ROOT / "docs" / "kanban" / "bounce_v5_contract.md").read_text(encoding="utf-8")

    assert "BV5-016" in contract
    assert "Option 2" in contract
    assert "bounce-v5-prototype" in contract
    assert "project-411e0419-48bd-4b5b-97f" in contract
    assert "asia-southeast1" in contract
