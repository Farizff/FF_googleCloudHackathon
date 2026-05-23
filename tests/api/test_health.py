from fastapi.testclient import TestClient

from api.main import app


def test_health_endpoint_returns_bounce_status():
    """Health endpoint must prove the backend is alive before adding features."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "Bounce", "version": "v0"}
