"""Tests for GET /settlements/{trip_id} endpoint and the underlying calculate_settlement logic."""
from uuid import uuid4

from fastapi.testclient import TestClient

from api.main import app
from api.routes.expenses import LogExpenseRequest, log_expense


class FakeCollection:
    def __init__(self, records=None):
        self.records = records or []
        self.find_queries = []
        self.find_one_queries = []
        self.inserted = []

    def find(self, query):
        self.find_queries.append(query)
        return [record for record in self.records if all(record.get(k) == v for k, v in query.items())]

    def find_one(self, query):
        self.find_one_queries.append(query)
        for record in self.records:
            if all(record.get(k) == v for k, v in query.items()):
                return record
        return None

    def insert_one(self, document):
        self.inserted.append(document)
        self.records.append(document)
        return None


class FakeDB:
    def __init__(self, expenses=None, trips=None, flocks=None):
        self.expenses = FakeCollection(expenses or [])
        self.group_trips = FakeCollection(trips or [])
        self.flocks = FakeCollection(flocks or [])


# ---------------------------------------------------------------------------
# Unit tests for calculate_settlement
# ---------------------------------------------------------------------------

def test_calculate_settlement_returns_minimum_transactions():
    """Two expenses across equal and custom splits should net to minimum transactions."""
    db = FakeDB(
        expenses=[
            {
                "trip_id": "trip_tokyo",
                "logged_by_user_id": "alex",
                "amount_usd": 90.0,
                "split_type": "equal",
                "participants": ["alex", "priya", "carlos"],
            },
            {
                "trip_id": "trip_tokyo",
                "logged_by_user_id": "priya",
                "amount_usd": 60.0,
                "split_type": "custom",
                "custom_splits": [
                    {"user_id": "alex", "amount_usd": 10.0},
                    {"user_id": "priya", "amount_usd": 20.0},
                    {"user_id": "carlos", "amount_usd": 30.0},
                ],
            },
        ]
    )

    from api.routes.expenses import calculate_settlement

    result = calculate_settlement("trip_tokyo", db)

    assert result["balances"] == {"alex": 50.0, "priya": 10.0, "carlos": -60.0}
    assert result["transactions"] == [
        {"from": "carlos", "to": "alex", "amount_usd": 50.0},
        {"from": "carlos", "to": "priya", "amount_usd": 10.0},
    ]


def test_calculate_settlement_rounds_small_dust():
    """Very small residual amounts (< $0.01) should be dropped, not rounded up."""
    db = FakeDB(
        expenses=[
            {
                "trip_id": "trip_tokyo",
                "logged_by_user_id": "alex",
                "amount_usd": 10.0,
                "split_type": "equal",
                "participants": ["alex", "priya", "carlos"],
            }
        ]
    )

    from api.routes.expenses import calculate_settlement

    result = calculate_settlement("trip_tokyo", db)

    assert result["balances"] == {"alex": 6.67, "priya": -3.33, "carlos": -3.33}
    assert result["transactions"] == [
        {"from": "priya", "to": "alex", "amount_usd": 3.33},
        {"from": "carlos", "to": "alex", "amount_usd": 3.33},
    ]


def test_calculate_settlement_empty_trip():
    """A trip with no expenses should return empty balances and no transactions."""
    db = FakeDB(expenses=[])

    from api.routes.expenses import calculate_settlement

    result = calculate_settlement("trip_tokyo", db)

    assert result["balances"] == {}
    assert result["transactions"] == []


def test_calculate_settlement_one_person_covers_all():
    """When one person pays for everyone else, they should receive from all debtors."""
    db = FakeDB(
        expenses=[
            {
                "trip_id": "trip_tokyo",
                "logged_by_user_id": "alex",
                "amount_usd": 120.0,
                "split_type": "equal",
                "participants": ["alex", "priya", "carlos", "emma"],
            }
        ]
    )

    from api.routes.expenses import calculate_settlement

    result = calculate_settlement("trip_tokyo", db)

    assert result["balances"] == {"alex": 90.0, "priya": -30.0, "carlos": -30.0, "emma": -30.0}
    assert result["transactions"] == [
        {"from": "priya", "to": "alex", "amount_usd": 30.0},
        {"from": "carlos", "to": "alex", "amount_usd": 30.0},
        {"from": "emma", "to": "alex", "amount_usd": 30.0},
    ]


def test_log_expense_everyone_normalizes_trip_members_to_user_ids():
    db = FakeDB(
        trips=[
            {
                "trip_id": "trip_tokyo",
                "members": [
                    {"user_id": "alex", "name": "Alex"},
                    {"user_id": "priya", "name": "Priya"},
                    {"user_id": "carlos", "name": "Carlos"},
                ],
            }
        ]
    )

    result = log_expense(
        trip_id="trip_tokyo",
        logged_by_user_id="alex",
        amount=90,
        currency="USD",
        category="Food",
        description="Ramen dinner",
        logging_mode="everyone",
        db=db,
        exchange_rate_fn=lambda _currency: 1,
        uuid_fn=lambda: "expense_fixed",
        clock=lambda: "2026-07-04T09:00:00Z",
    )

    assert result["success"] is True
    assert result["participants"] == ["alex", "priya", "carlos"]
    assert db.expenses.inserted[0]["participants"] == ["alex", "priya", "carlos"]
