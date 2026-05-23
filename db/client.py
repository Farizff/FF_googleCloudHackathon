from collections.abc import Callable
from typing import Any

from pymongo import MongoClient

from api.settings import AppSettings, get_settings


class MongoDBConfigError(RuntimeError):
    """Raised when Bounce cannot safely create a MongoDB connection."""


def get_database(
    settings: AppSettings | None = None,
    client_factory: Callable[..., Any] = MongoClient,
) -> Any:
    """Create and return the configured MongoDB database handle.

    The helper fails loudly when credentials are missing. Tests can inject a
    fake `client_factory` so they never contact MongoDB Atlas.
    """
    resolved_settings = settings or get_settings()
    connection_string = resolved_settings.mongodb_connection_string.strip()

    if not connection_string:
        raise MongoDBConfigError(
            "MONGODB_CONNECTION_STRING is required before connecting to MongoDB. "
            "Set it locally or provide the mongodb-uri secret in Cloud Run."
        )

    client = client_factory(connection_string, serverSelectionTimeoutMS=3000)
    return client[resolved_settings.mongodb_database]
