from api.settings import AppSettings


def test_settings_default_to_prd_v2_deployment_values():
    """Defaults must keep local and Cloud Run work pointed at the PRD v2.1 target."""
    settings = AppSettings()

    assert settings.gcp_project_id == "bounce-hackathon-2026"
    assert settings.gcp_region == "asia-southeast1"
    assert settings.mongodb_database == "bounce"
    assert settings.amadeus_hostname == "production"


def test_settings_can_be_overridden_by_environment(monkeypatch):
    """Cloud Run secrets and local env vars must override safe defaults."""
    monkeypatch.setenv("GCP_PROJECT_ID", "custom-project")
    monkeypatch.setenv("MONGODB_DATABASE", "bounce_test")
    monkeypatch.setenv("MONGODB_CONNECTION_STRING", "mongodb+srv://example")

    settings = AppSettings()

    assert settings.gcp_project_id == "custom-project"
    assert settings.mongodb_database == "bounce_test"
    assert settings.mongodb_connection_string == "mongodb+srv://example"
