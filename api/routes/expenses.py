from datetime import UTC, datetime
from typing import Any, Callable
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from db.client import get_database

router = APIRouter(prefix="/expenses", tags=["expenses"])


TRIP_NOT_FOUND = "TRIP_NOT_FOUND"
FLOCK_NOT_FOUND = "FLOCK_NOT_FOUND"
INVALID_LOGGING_MODE = "INVALID_LOGGING_MODE"


class LogExpenseRequest(BaseModel):
    trip_id: str
    logged_by_user_id: str
    amount: float
    currency: str
    category: str
    description: str
    logging_mode: str
    participants: list[str] | None = None
    flock_id: str | None = None
    split_type: str = "equal"
    custom_splits: list[dict[str, Any]] | None = None
    day_number: int | None = None


def get_db() -> Any:
    return get_database()


def calculate_settlement(trip_id: str, db: Any) -> dict[str, Any]:
    """Return minimum-transaction settlement plan for a trip."""
    expenses = list(db.expenses.find({"trip_id": trip_id}))
    balances: dict[str, float] = {}

    for expense in expenses:
        payer = expense["logged_by_user_id"]
        amount = float(expense["amount_usd"])
        balances[payer] = balances.get(payer, 0.0) + amount

        if expense.get("split_type") == "custom":
            for split in expense.get("custom_splits", []):
                user_id = split["user_id"]
                balances[user_id] = balances.get(user_id, 0.0) - float(split["amount_usd"])
        else:
            participants = expense.get("participants", [])
            if not participants:
                continue
            share = amount / len(participants)
            for user_id in participants:
                balances[user_id] = balances.get(user_id, 0.0) - share

    rounded_balances = {user_id: round(balance, 2) for user_id, balance in balances.items()}
    return {
        "balances": rounded_balances,
        "transactions": _minimum_transactions(rounded_balances),
    }


def log_expense(
    trip_id: str,
    logged_by_user_id: str,
    amount: float,
    currency: str,
    category: str,
    description: str,
    logging_mode: str,
    db: Any,
    exchange_rate_fn: Callable[[str], float],
    *,
    participants: list[str] | None = None,
    flock_id: str | None = None,
    split_type: str = "equal",
    custom_splits: list[dict[str, Any]] | None = None,
    day_number: int | None = None,
    uuid_fn: Callable[[], str] | None = None,
    clock: Callable[[], str] | None = None,
) -> dict[str, Any]:
    """Persist a manual split-bill expense for the four demo logging modes."""
    trip = db.group_trips.find_one({"trip_id": trip_id})
    if trip is None:
        return _error(TRIP_NOT_FOUND, f"Trip not found for trip_id '{trip_id}'.")

    resolved_participants = _resolve_participants(
        logging_mode=logging_mode,
        logged_by_user_id=logged_by_user_id,
        provided_participants=participants,
        trip=trip,
        trip_id=trip_id,
        flock_id=flock_id,
        db=db,
    )
    if isinstance(resolved_participants, dict) and "error" in resolved_participants:
        return resolved_participants

    rate = float(exchange_rate_fn(currency))
    amount_usd = round(float(amount) * rate, 2)
    expense_id = (uuid_fn or (lambda: str(uuid4())))()
    logged_at = (clock or _utc_now_iso)()
    expense = {
        "expense_id": expense_id,
        "trip_id": trip_id,
        "logged_by_user_id": logged_by_user_id,
        "logged_at": logged_at,
        "amount": amount,
        "currency": currency,
        "amount_usd": amount_usd,
        "exchange_rate_used": rate,
        "category": category,
        "description": description,
        "flock_id": flock_id,
        "logging_mode": logging_mode,
        "participants": resolved_participants,
        "split_type": split_type,
        "custom_splits": custom_splits or [],
        "day_number": day_number,
    }
    db.expenses.insert_one(expense)

    return {
        "expense_id": expense_id,
        "success": True,
        "amount_usd": amount_usd,
        "participants": resolved_participants,
    }


def _minimum_transactions(balances: dict[str, float]) -> list[dict[str, Any]]:
    creditors = sorted(
        [(user_id, balance) for user_id, balance in balances.items() if balance > 0],
        key=lambda item: -item[1],
    )
    debtors = sorted(
        [(user_id, -balance) for user_id, balance in balances.items() if balance < 0],
        key=lambda item: -item[1],
    )

    transactions = []
    while creditors and debtors:
        creditor_id, creditor_amount = creditors.pop(0)
        debtor_id, debtor_amount = debtors.pop(0)
        transfer = round(min(creditor_amount, debtor_amount), 2)
        if transfer > 0.01:
            transactions.append({"from": debtor_id, "to": creditor_id, "amount_usd": transfer})

        remaining_credit = round(creditor_amount - transfer, 2)
        remaining_debt = round(debtor_amount - transfer, 2)
        if remaining_credit > 0.01:
            creditors.insert(0, (creditor_id, remaining_credit))
        if remaining_debt > 0.01:
            debtors.insert(0, (debtor_id, remaining_debt))

    return transactions


def _participant_user_ids(members: list[Any]) -> list[str]:
    user_ids: list[str] = []
    for member in members:
        if isinstance(member, dict):
            user_id = member.get("user_id")
            if user_id:
                user_ids.append(str(user_id))
        elif member:
            user_ids.append(str(member))
    return user_ids


def _resolve_participants(
    logging_mode: str,
    logged_by_user_id: str,
    provided_participants: list[str] | None,
    trip: dict[str, Any],
    trip_id: str,
    flock_id: str | None,
    db: Any,
) -> list[str] | dict[str, dict[str, str]]:
    if logging_mode == "everyone":
        return _participant_user_ids(list(trip.get("members", [])))
    if logging_mode == "specific_people":
        return list(provided_participants or [])
    if logging_mode == "just_me":
        return [logged_by_user_id]
    if logging_mode == "my_flock":
        flock = db.flocks.find_one({"trip_id": trip_id, "flock_id": flock_id})
        if flock is None:
            return _error(FLOCK_NOT_FOUND, f"Flock not found for flock_id '{flock_id}'.")
        return list(flock.get("members", []))
    return _error(INVALID_LOGGING_MODE, f"Unsupported logging_mode '{logging_mode}'.")


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _error(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


@router.post("")
def log_expense_endpoint(request: LogExpenseRequest, db: Any = Depends(get_db)) -> dict[str, Any]:
    """Persist a split-bill expense for a trip."""
    result = log_expense(
        trip_id=request.trip_id,
        logged_by_user_id=request.logged_by_user_id,
        amount=request.amount,
        currency=request.currency,
        category=request.category,
        description=request.description,
        logging_mode=request.logging_mode,
        db=db,
        exchange_rate_fn=lambda c: 1.0,  # Placeholder; real rates injected in tests
        participants=request.participants,
        flock_id=request.flock_id,
        split_type=request.split_type,
        custom_splits=request.custom_splits,
        day_number=request.day_number,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
