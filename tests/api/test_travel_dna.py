"""Tests for GET /travel-dna/{user_id} endpoint and compute_travel_dna logic."""
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from api.routes.travel_dna import compute_travel_dna


# ---------------------------------------------------------------------------
# Unit tests for compute_travel_dna (pure function)
# ---------------------------------------------------------------------------

def test_adrenaline_junkie_pace_packed_nightlife():
    profile = {
        "preferences": {"pace": "packed", "interests": ["nightlife", "music"], "crowd_tolerance": "tolerate"},
        "physical_fitness": "high",
    }
    assert compute_travel_dna(profile) == "adrenaline_junkie"


def test_adrenaline_junkie_pace_packed_sport():
    profile = {
        "preferences": {"pace": "packed", "interests": ["sport", "shopping"], "crowd_tolerance": "neutral"},
        "physical_fitness": "high",
    }
    assert compute_travel_dna(profile) == "adrenaline_junkie"


def test_zen_explorer_relaxed_nature():
    profile = {
        "preferences": {"pace": "relaxed", "interests": ["nature", "wellness"], "crowd_tolerance": "neutral"},
        "physical_fitness": "average",
    }
    assert compute_travel_dna(profile) == "zen_explorer"


def test_zen_explorer_relaxed_wellness():
    profile = {
        "preferences": {"pace": "relaxed", "interests": ["wellness", "food"], "crowd_tolerance": "prefer_empty"},
        "physical_fitness": "low",
    }
    assert compute_travel_dna(profile) == "zen_explorer"


def test_cultural_connoisseur_moderate_culture():
    profile = {
        "preferences": {"pace": "moderate", "interests": ["culture", "art"], "crowd_tolerance": "tolerate"},
        "physical_fitness": "average",
    }
    assert compute_travel_dna(profile) == "cultural_connoisseur"


def test_cultural_connoisseur_moderate_history():
    profile = {
        "preferences": {"pace": "moderate", "interests": ["history", "architecture"], "crowd_tolerance": "neutral"},
        "physical_fitness": "high",
    }
    assert compute_travel_dna(profile) == "cultural_connoisseur"


def test_foodie_adventurer_food_tolerate():
    profile = {
        "preferences": {"pace": "moderate", "interests": ["food", "shopping"], "crowd_tolerance": "tolerate"},
        "physical_fitness": "average",
    }
    assert compute_travel_dna(profile) == "foodie_adventurer"


def test_balanced_explorer_default():
    profile = {
        "preferences": {"pace": "moderate", "interests": ["shopping", "architecture"], "crowd_tolerance": "neutral"},
        "physical_fitness": "average",
    }
    assert compute_travel_dna(profile) == "balanced_explorer"


def test_balanced_explorer_relaxed_no_nature():
    profile = {
        "preferences": {"pace": "relaxed", "interests": ["shopping", "music"], "crowd_tolerance": "prefer_empty"},
        "physical_fitness": "low",
    }
    assert compute_travel_dna(profile) == "balanced_explorer"


def test_balanced_explorer_packed_no_nightlife_sport():
    profile = {
        "preferences": {"pace": "packed", "interests": ["food", "architecture"], "crowd_tolerance": "neutral"},
        "physical_fitness": "high",
    }
    assert compute_travel_dna(profile) == "balanced_explorer"


# ---------------------------------------------------------------------------
# Integration-style tests for the endpoint (mocked DB)
# ---------------------------------------------------------------------------

class FakeCollection:
    def __init__(self, records=None):
        self.records = records or []
        self.find_queries = []
        self.find_one_queries = []
        self.updated = []

    def find_one(self, query):
        self.find_one_queries.append(query)
        for record in self.records:
            if all(record.get(k) == v for k, v in query.items()):
                return record
        return None

    def update_one(self, query, update):
        self.find_one_queries.append(query)
        for record in self.records:
            if all(record.get(k) == v for k, v in query.items()):
                record.update(update.get("$set", {}))
                self.updated.append(record)
                return None
        return None


class FakeDB:
    def __init__(self):
        self.traveller_profiles = FakeCollection()


def test_travel_dna_endpoint_returns_404_for_missing_profile():
    from fastapi.testclient import TestClient
    from api.main import app

    # Override the get_database dependency
    app.dependency_overrides[__import__('api.routes.travel_dna', fromlist=['get_db']).get_db] = lambda: FakeDB()

    client = TestClient(app)
    response = client.get("/travel-dna/u_unknown")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "PROFILE_NOT_FOUND"

    app.dependency_overrides.clear()


def test_travel_dna_endpoint_computes_and_stores_dna():
    from fastapi.testclient import TestClient
    from api.main import app

    fake_db = FakeDB()
    fake_db.traveller_profiles.records = [
        {
            "user_id": "u_marcus",
            "name": "Marcus Johnson",
            "preferences": {
                "pace": "packed",
                "interests": ["food", "nightlife", "music"],
                "crowd_tolerance": "tolerate",
            },
            "physical_fitness": "high",
        }
    ]

    app.dependency_overrides[__import__('api.routes.travel_dna', fromlist=['get_db']).get_db] = lambda: fake_db

    client = TestClient(app)
    response = client.get("/travel-dna/u_marcus")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "u_marcus"
    assert data["travel_dna"]["primary_style"] == "adrenaline_junkie"
    assert data["travel_dna"]["energy_level"] == "high"
    assert "last_updated" in data["travel_dna"]

    app.dependency_overrides.clear()


def test_travel_dna_endpoint_stores_result_in_profile():
    from fastapi.testclient import TestClient
    from api.main import app

    fake_db = FakeDB()
    profile_record = {
        "user_id": "u_priya",
        "name": "Priya Patel",
        "preferences": {"pace": "moderate", "interests": ["culture", "art", "history"], "crowd_tolerance": "tolerate"},
        "physical_fitness": "average",
    }
    fake_db.traveller_profiles.records = [profile_record]

    app.dependency_overrides[__import__('api.routes.travel_dna', fromlist=['get_db']).get_db] = lambda: fake_db

    client = TestClient(app)
    response = client.get("/travel-dna/u_priya")

    assert response.status_code == 200
    assert response.json()["travel_dna"]["primary_style"] == "cultural_connoisseur"
    # Verify update was called
    assert len(fake_db.traveller_profiles.updated) == 1
    updated = fake_db.traveller_profiles.updated[0]
    assert updated["travel_dna"]["primary_style"] == "cultural_connoisseur"

    app.dependency_overrides.clear()