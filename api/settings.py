from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Runtime configuration for Bounce.

    Defaults mirror PRD v2.1 and `.env.example`; secrets stay blank until
    supplied by local environment variables or Cloud Run Secret Manager.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gcp_project_id: str = "bounce-hackathon-2026"
    gcp_region: str = "asia-southeast1"
    agent_builder_agent_id: str = ""

    mongodb_connection_string: str = ""
    mongodb_database: str = "bounce"

    firebase_database_url: str = "https://bounce-hackathon-2026-default-rtdb.firebaseio.com/"
    firebase_service_account_key: str = ""

    google_maps_api_key: str = ""
    gemini_api_key: str = ""

    amadeus_client_id: str = ""
    amadeus_client_secret: str = ""
    amadeus_hostname: str = "production"

    rapidapi_key: str = ""
    aerodatabox_host: str = "aerodatabox.p.rapidapi.com"

    opensky_username: str = ""
    opensky_password: str = ""
    rome2rio_api_key: str = ""

    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "bounce@yourdomain.com"

    exchange_rate_api_key: str = ""


def get_settings() -> AppSettings:
    """Return settings loaded from environment and optional local `.env`."""
    return AppSettings()
