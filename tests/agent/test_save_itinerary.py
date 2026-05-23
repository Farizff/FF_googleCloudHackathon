from agent.tools.save_itinerary import save_itinerary


class FakeItinerariesCollection:
    def __init__(self):
        self.updates = []
        self.documents = {}

    def update_one(self, query, update, upsert=False):
        self.updates.append({"query": query, "update": update, "upsert": upsert})
        document = update["$set"]
        self.documents[query["itinerary_id"]] = document
        return {"acknowledged": True}


class FakeFirebaseBroadcaster:
    def __init__(self):
        self.broadcasts = []

    def broadcast_itinerary_saved(self, itinerary):
        self.broadcasts.append(itinerary)


def fixed_clock():
    return "2026-05-23T10:15:30Z"


def test_save_itinerary_inserts_new_itinerary_with_injected_id_and_timestamp():
    """New itineraries should be upserted into the injected collection without live Firebase."""
    collection = FakeItinerariesCollection()
    itinerary = {
        "trip_id": "trip_tokyo_demo",
        "days": [{"day_number": 1, "stops": ["place_sensoji"]}],
    }

    result = save_itinerary(
        itinerary=itinerary,
        collection=collection,
        clock=fixed_clock,
        id_factory=lambda: "iti_tokyo_demo",
    )

    expected_document = {
        "trip_id": "trip_tokyo_demo",
        "days": [{"day_number": 1, "stops": ["place_sensoji"]}],
        "itinerary_id": "iti_tokyo_demo",
        "updated_at": "2026-05-23T10:15:30Z",
    }
    assert result == {
        "success": True,
        "itinerary_id": "iti_tokyo_demo",
        "updated_at": "2026-05-23T10:15:30Z",
    }
    assert collection.updates == [
        {
            "query": {"itinerary_id": "iti_tokyo_demo"},
            "update": {"$set": expected_document},
            "upsert": True,
        }
    ]
    assert collection.documents["iti_tokyo_demo"] == expected_document


def test_save_itinerary_updates_existing_itinerary_and_broadcasts_through_stub():
    """Existing itinerary ids should be preserved and Firebase broadcasting should be injectable."""
    collection = FakeItinerariesCollection()
    firebase = FakeFirebaseBroadcaster()
    itinerary = {
        "itinerary_id": "iti_existing",
        "trip_id": "trip_tokyo_demo",
        "days": [{"day_number": 2, "stops": ["place_meiji"]}],
        "updated_at": "old_timestamp",
    }

    result = save_itinerary(
        itinerary=itinerary,
        collection=collection,
        firebase_broadcaster=firebase,
        clock=fixed_clock,
        id_factory=lambda: "should_not_be_used",
    )

    saved_document = collection.documents["iti_existing"]
    assert result == {
        "success": True,
        "itinerary_id": "iti_existing",
        "updated_at": "2026-05-23T10:15:30Z",
    }
    assert collection.updates == [
        {
            "query": {"itinerary_id": "iti_existing"},
            "update": {"$set": saved_document},
            "upsert": True,
        }
    ]
    assert saved_document["updated_at"] == "2026-05-23T10:15:30Z"
    assert firebase.broadcasts == [saved_document]
