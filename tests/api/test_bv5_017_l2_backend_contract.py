from fastapi.testclient import TestClient

from api.main import app


def test_health_endpoint_can_report_v5_shape_when_l2_mode_enabled(monkeypatch):
    monkeypatch.setenv("BOUNCE_API_MODE", "v5")
    monkeypatch.setenv("MONGODB_CONNECTION_STRING", "mongodb+srv://example.invalid/bounce")
    monkeypatch.setenv("FIREBASE_DATABASE_URL", "https://bounce-example.firebaseio.com")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "Bounce",
        "version": "v5",
        "mongo": "configured",
        "firebase": "configured",
        "mode": "l2",
    }


def test_v5_l2_backend_contract_records_sse_deferral_and_provider_names():
    contract_path = app.root_path  # keeps import used while real path is resolved below
    del contract_path
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    contract = (root / "docs" / "architecture" / "bounce_v5_l2_backend_contract.md").read_text(encoding="utf-8")

    assert "POST `/api/chat`" in contract
    assert "SSE streaming" in contract
    assert "explicitly deferred" in contract
    for collection in [
        "group_trips",
        "itineraries",
        "expenses",
        "suggestions",
        "traveller_profiles",
        "flights",
    ]:
        assert f"`{collection}`" in contract
    for path in [
        "trips/{tripId}/members/{memberId}/location",
        "trips/{tripId}/alerts",
        "trips/{tripId}/flock_status",
    ]:
        assert f"`{path}`" in contract
