from api.routes.expenses import calculate_settlement, log_expense


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


def test_calculate_settlement_returns_minimum_transactions_for_equal_and_custom_splits():
    db = FakeDB(
        expenses=[
            {
                "trip_id": "trip_tokyo",
                "logged_by_user_id": "alex",
                "amount_usd": 90,
                "split_type": "equal",
                "participants": ["alex", "priya", "carlos"],
            },
            {
                "trip_id": "trip_tokyo",
                "logged_by_user_id": "priya",
                "amount_usd": 60,
                "split_type": "custom",
                "custom_splits": [
                    {"user_id": "alex", "amount_usd": 10},
                    {"user_id": "priya", "amount_usd": 20},
                    {"user_id": "carlos", "amount_usd": 30},
                ],
            },
        ]
    )

    result = calculate_settlement("trip_tokyo", db)

    assert result == {
        "balances": {"alex": 50.0, "priya": 10.0, "carlos": -60.0},
        "transactions": [
            {"from": "carlos", "to": "alex", "amount_usd": 50.0},
            {"from": "carlos", "to": "priya", "amount_usd": 10.0},
        ],
    }


def test_calculate_settlement_ignores_balanced_small_rounding_dust():
    db = FakeDB(
        expenses=[
            {
                "trip_id": "trip_tokyo",
                "logged_by_user_id": "alex",
                "amount_usd": 10,
                "split_type": "equal",
                "participants": ["alex", "priya", "carlos"],
            }
        ]
    )

    result = calculate_settlement("trip_tokyo", db)

    assert result["balances"] == {"alex": 6.67, "priya": -3.33, "carlos": -3.33}
    assert result["transactions"] == [
        {"from": "priya", "to": "alex", "amount_usd": 3.33},
        {"from": "carlos", "to": "alex", "amount_usd": 3.33},
    ]


def test_log_expense_everyone_mode_uses_all_trip_members_and_converts_currency():
    db = FakeDB(trips=[{"trip_id": "trip_tokyo", "members": ["alex", "priya", "carlos"]}])

    result = log_expense(
        trip_id="trip_tokyo",
        logged_by_user_id="alex",
        amount=12000,
        currency="JPY",
        category="food",
        description="Ramen dinner",
        logging_mode="everyone",
        db=db,
        exchange_rate_fn=lambda currency: 0.0067,
        uuid_fn=lambda: "expense_1",
        clock=lambda: "2026-07-04T12:00:00Z",
    )

    assert result == {"expense_id": "expense_1", "success": True, "amount_usd": 80.4, "participants": ["alex", "priya", "carlos"]}
    assert db.expenses.inserted == [
        {
            "expense_id": "expense_1",
            "trip_id": "trip_tokyo",
            "logged_by_user_id": "alex",
            "logged_at": "2026-07-04T12:00:00Z",
            "amount": 12000,
            "currency": "JPY",
            "amount_usd": 80.4,
            "exchange_rate_used": 0.0067,
            "category": "food",
            "description": "Ramen dinner",
            "flock_id": None,
            "logging_mode": "everyone",
            "participants": ["alex", "priya", "carlos"],
            "split_type": "equal",
            "custom_splits": [],
            "day_number": None,
        }
    ]


def test_log_expense_supports_specific_people_my_flock_and_just_me_modes():
    db = FakeDB(
        trips=[{"trip_id": "trip_tokyo", "members": ["alex", "priya", "carlos", "emma"]}],
        flocks=[{"trip_id": "trip_tokyo", "flock_id": "flock_food", "members": ["alex", "emma"]}],
    )

    specific = log_expense("trip_tokyo", "alex", 30, "USD", "transport", "Taxi", "specific_people", db, lambda c: 1, participants=["alex", "priya"], uuid_fn=lambda: "specific", clock=lambda: "now")
    flock = log_expense("trip_tokyo", "alex", 50, "USD", "activity", "Museum", "my_flock", db, lambda c: 1, flock_id="flock_food", uuid_fn=lambda: "flock", clock=lambda: "now")
    solo = log_expense("trip_tokyo", "alex", 12, "USD", "shopping", "Snack", "just_me", db, lambda c: 1, uuid_fn=lambda: "solo", clock=lambda: "now")

    assert specific["participants"] == ["alex", "priya"]
    assert flock["participants"] == ["alex", "emma"]
    assert solo["participants"] == ["alex"]


def test_log_expense_returns_standard_error_for_missing_trip_or_flock():
    db = FakeDB(trips=[])

    missing_trip = log_expense("missing", "alex", 10, "USD", "food", "Coffee", "everyone", db, lambda c: 1)

    assert missing_trip["error"]["code"] == "TRIP_NOT_FOUND"

    db = FakeDB(trips=[{"trip_id": "trip_tokyo", "members": ["alex"]}], flocks=[])
    missing_flock = log_expense("trip_tokyo", "alex", 10, "USD", "food", "Coffee", "my_flock", db, lambda c: 1, flock_id="missing")

    assert missing_flock["error"]["code"] == "FLOCK_NOT_FOUND"
