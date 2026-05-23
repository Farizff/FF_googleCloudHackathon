from agent.tools.get_visa_requirements import get_visa_requirements


class FakeVisaCollection:
    def __init__(self, records=None):
        self.records = records or []
        self.find_one_queries = []
        self.update_one_calls = []

    def find_one(self, query):
        self.find_one_queries.append(query)
        for record in self.records:
            if all(record.get(key) == value for key, value in query.items()):
                return dict(record)
        return None

    def update_one(self, query, update, upsert=False):
        self.update_one_calls.append({"query": query, "update": update, "upsert": upsert})


def ind_jpn_record(**overrides):
    record = {
        "passport_iso": "IND",
        "destination_iso": "JPN",
        "visa_required": True,
        "visa_type": "consulate-visa",
        "processing_days_min": 5,
        "processing_days_max": 14,
        "official_url": "https://www.mofa.go.jp/j_info/visit/visa/index.html",
        "fee_usd_estimate": 25,
        "notes": "Standard tourist visa.",
        "last_verified": "2026-05-01",
    }
    record.update(overrides)
    return record


def test_get_visa_requirements_returns_fresh_mongo_hit_with_embassy_note():
    collection = FakeVisaCollection([ind_jpn_record()])

    result = get_visa_requirements(
        "ind",
        "jpn",
        visa_requirements_collection=collection,
        clock=lambda: "2026-05-23",
    )

    assert result == {
        "passport_iso": "IND",
        "destination_iso": "JPN",
        "visa_required": True,
        "visa_type": "consulate-visa",
        "processing_days_min": 5,
        "processing_days_max": 14,
        "official_url": "https://www.mofa.go.jp/j_info/visit/visa/index.html",
        "fee_usd_estimate": 25,
        "notes": "Standard tourist visa. Verify with the embassy — requirements may change.",
        "last_verified": "2026-05-01",
        "source": "mongo",
    }
    assert collection.find_one_queries == [{"passport_iso": "IND", "destination_iso": "JPN"}]
    assert collection.update_one_calls == []


def test_get_visa_requirements_uses_fallback_for_stale_record_and_caches_result():
    collection = FakeVisaCollection([ind_jpn_record(last_verified="2025-12-01")])
    fallback_calls = []

    def fallback(passport_iso, destination_iso):
        fallback_calls.append((passport_iso, destination_iso))
        return {
            "passport_iso": passport_iso,
            "destination_iso": destination_iso,
            "visa_required": True,
            "visa_type": "consulate-visa",
            "processing_days_min": 10,
            "processing_days_max": 14,
            "official_url": "https://www.indembassy-tokyo.gov.in/",
            "fee_usd_estimate": 25,
            "notes": "Apply through the embassy portal.",
        }

    result = get_visa_requirements(
        "IND",
        "JPN",
        visa_requirements_collection=collection,
        web_search_fn=fallback,
        clock=lambda: "2026-05-23",
    )

    assert fallback_calls == [("IND", "JPN")]
    assert result["source"] == "fallback"
    assert result["last_verified"] == "2026-05-23"
    assert result["cache_ttl_days"] == 30
    assert result["notes"].endswith("Verify with the embassy — requirements may change.")
    assert collection.update_one_calls == [
        {
            "query": {"passport_iso": "IND", "destination_iso": "JPN"},
            "update": {"$set": {key: result[key] for key in result if key != "source"}},
            "upsert": True,
        }
    ]


def test_get_visa_requirements_normalizes_iso_codes_before_lookup_and_fallback():
    collection = FakeVisaCollection([])
    fallback_calls = []

    def fallback(passport_iso, destination_iso):
        fallback_calls.append((passport_iso, destination_iso))
        return ind_jpn_record(passport_iso=passport_iso, destination_iso=destination_iso)

    result = get_visa_requirements(
        " inD ",
        " jpN ",
        visa_requirements_collection=collection,
        web_search_fn=fallback,
        clock=lambda: "2026-05-23",
    )

    assert collection.find_one_queries == [{"passport_iso": "IND", "destination_iso": "JPN"}]
    assert fallback_calls == [("IND", "JPN")]
    assert result["passport_iso"] == "IND"
    assert result["destination_iso"] == "JPN"


def test_get_visa_requirements_does_not_duplicate_existing_embassy_verification_note():
    collection = FakeVisaCollection(
        [ind_jpn_record(notes="Verify with the embassy — requirements may change.")]
    )

    result = get_visa_requirements(
        "IND",
        "JPN",
        visa_requirements_collection=collection,
        clock=lambda: "2026-05-23",
    )

    assert result["notes"] == "Verify with the embassy — requirements may change."


def test_get_visa_requirements_returns_standard_error_when_fallback_unavailable_or_invalid():
    missing = get_visa_requirements(
        "XYZ",
        "JPN",
        visa_requirements_collection=FakeVisaCollection([]),
        clock=lambda: "2026-05-23",
    )
    invalid = get_visa_requirements(
        "XYZ",
        "JPN",
        visa_requirements_collection=FakeVisaCollection([]),
        web_search_fn=lambda passport_iso, destination_iso: {"passport_iso": passport_iso},
        clock=lambda: "2026-05-23",
    )

    assert missing == {
        "error": {
            "code": "VISA_REQUIREMENTS_UNAVAILABLE",
            "message": "Visa requirements unavailable for XYZ to JPN.",
        }
    }
    assert invalid == missing
