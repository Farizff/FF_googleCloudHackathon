from agent.tools.get_traveller_profile import get_traveller_profile


class FakeTravellerProfilesCollection:
    def __init__(self, documents):
        self.documents = {document["user_id"]: document for document in documents}
        self.queries = []

    def find_one(self, query):
        self.queries.append(query)
        return self.documents.get(query["user_id"])


def test_get_traveller_profile_returns_matching_profile_from_injected_collection():
    """The tool should fetch the exact traveller profile by user_id without live MongoDB."""
    alex_profile = {
        "user_id": "usr_alex",
        "name": "Alex Chen",
        "passport_country": "USA",
        "dietary": {"restrictions": ["none"], "allergies": [], "strictness": "flexible"},
        "preferences": {"pace": "moderate", "wake_time": "08:00", "interests": ["food"], "crowd_tolerance": "tolerate"},
    }
    collection = FakeTravellerProfilesCollection([alex_profile])

    result = get_traveller_profile(user_id="usr_alex", collection=collection)

    assert result == {"profile": alex_profile}
    assert collection.queries == [{"user_id": "usr_alex"}]


def test_get_traveller_profile_returns_standard_user_not_found_error():
    """Unknown users should return Bounce's standard tool error shape."""
    collection = FakeTravellerProfilesCollection([])

    result = get_traveller_profile(user_id="missing_user", collection=collection)

    assert result == {
        "error": {
            "code": "USER_NOT_FOUND",
            "message": "Traveller profile not found for user_id 'missing_user'.",
        }
    }
    assert collection.queries == [{"user_id": "missing_user"}]
