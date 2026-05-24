from scripts.infra.verify_mongodb_atlas import (
    EXPECTED_COLLECTIONS,
    ensure_expected_collections,
    run_write_probe,
    verify_mongodb_atlas,
)


class FakeCollection:
    def __init__(self):
        self.documents = []

    def delete_many(self, query):
        self.documents = [doc for doc in self.documents if not all(doc.get(k) == v for k, v in query.items())]

    def insert_one(self, document):
        self.documents.append(dict(document))

    def find_one(self, query):
        for document in self.documents:
            if all(document.get(k) == v for k, v in query.items()):
                return document
        return None


class FakeDatabase:
    def __init__(self, initial_collections=()):
        self.collections = {name: FakeCollection() for name in initial_collections}

    def list_collection_names(self):
        return list(self.collections)

    def create_collection(self, name):
        self.collections.setdefault(name, FakeCollection())

    def __getitem__(self, name):
        self.collections.setdefault(name, FakeCollection())
        return self.collections[name]


class FakeAdmin:
    def __init__(self):
        self.commands = []

    def command(self, name):
        self.commands.append(name)
        return {"ok": 1}


class FakeClient:
    last_instance = None

    def __init__(self, uri, **kwargs):
        self.uri = uri
        self.kwargs = kwargs
        self.admin = FakeAdmin()
        self.databases = {"bounce": FakeDatabase(initial_collections=EXPECTED_COLLECTIONS[:-1])}
        FakeClient.last_instance = self

    def __getitem__(self, name):
        return self.databases.setdefault(name, FakeDatabase())


def test_ensure_expected_collections_reports_and_creates_missing_prd_collections():
    database = FakeDatabase(initial_collections=("traveller_profiles", "group_trips"))

    missing, created = ensure_expected_collections(database, create_missing=True)

    assert missing == EXPECTED_COLLECTIONS[2:]
    assert created == EXPECTED_COLLECTIONS[2:]
    assert set(database.list_collection_names()) == set(EXPECTED_COLLECTIONS)


def test_write_probe_uses_notification_log_and_cleans_up_marker():
    database = FakeDatabase(initial_collections=EXPECTED_COLLECTIONS)

    assert run_write_probe(database) is True
    assert database["notification_log"].documents == []


def test_verify_mongodb_atlas_pings_creates_missing_and_runs_probe_without_printing_uri():
    result = verify_mongodb_atlas(
        uri="mongodb+srv://example.invalid/redacted",
        database_name="bounce",
        create_missing=True,
        write_probe=True,
        client_factory=FakeClient,
    )

    assert FakeClient.last_instance.admin.commands == ["ping"]
    assert result.database == "bounce"
    assert result.missing_collections == ()
    assert result.created_collections == ("notification_log",)
    assert result.write_probe_ok is True
