import pytest

from api.settings import AppSettings
from db.client import MongoDBConfigError, get_database


class FakeMongoClient:
    def __init__(self, uri, serverSelectionTimeoutMS):
        self.uri = uri
        self.server_selection_timeout_ms = serverSelectionTimeoutMS
        self.requested_databases = []

    def __getitem__(self, database_name):
        self.requested_databases.append(database_name)
        return {"database_name": database_name, "uri": self.uri}


def test_get_database_fails_loud_when_connection_string_missing():
    """Missing MongoDB credentials should stop startup instead of silently using a fake DB."""
    settings = AppSettings(mongodb_connection_string="")

    with pytest.raises(MongoDBConfigError, match="MONGODB_CONNECTION_STRING"):
        get_database(settings=settings, client_factory=FakeMongoClient)


def test_get_database_uses_configured_database_and_short_timeout():
    """The Mongo helper should create a client from settings without making tests hit Atlas."""
    settings = AppSettings(
        mongodb_connection_string="mongodb+srv://example",
        mongodb_database="bounce_test",
    )

    database = get_database(settings=settings, client_factory=FakeMongoClient)

    assert database == {"database_name": "bounce_test", "uri": "mongodb+srv://example"}
