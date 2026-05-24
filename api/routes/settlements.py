from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db.client import get_database

router = APIRouter(prefix="/settlements", tags=["expenses"])


def get_db() -> Any:
    return get_database()


class SettlementResponse(BaseModel):
    trip_id: str
    balances: dict[str, float]
    transactions: list[dict[str, Any]]


@router.get("/{trip_id}", response_model=SettlementResponse)
def get_settlement(trip_id: str, db: Any = Depends(get_db)) -> dict[str, Any]:
    """Return minimum-transaction settlement plan for a trip."""
    trip = db.group_trips.find_one({"trip_id": trip_id})
    if trip is None:
        raise HTTPException(status_code=404, detail={"code": "TRIP_NOT_FOUND", "message": f"Trip '{trip_id}' not found."})

    # Import here to avoid circular imports
    from api.routes.expenses import calculate_settlement
    result = calculate_settlement(trip_id, db)
    return {"trip_id": trip_id, **result}