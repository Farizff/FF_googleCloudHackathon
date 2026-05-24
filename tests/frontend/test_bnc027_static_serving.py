from fastapi.testclient import TestClient

from api.main import app


def test_fastapi_serves_frontend_app_shell_at_root():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert '<main id="app"' in response.text
    assert 'src="app.js"' in response.text


def test_fastapi_serves_frontend_assets_for_same_origin_api_calls():
    client = TestClient(app)

    app_js = client.get("/app.js")
    manifest = client.get("/manifest.json")

    assert app_js.status_code == 200
    assert "async function checkHealth" in app_js.text
    assert manifest.status_code == 200
    assert manifest.json()["name"] == "Bounce"
