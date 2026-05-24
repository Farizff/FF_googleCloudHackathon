from datetime import UTC, datetime
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException

from db.client import get_database
from workers.flight_poller import poll_active_trip_flights
from workers.reminder_dispatcher import dispatch_due_reminders

router = APIRouter(prefix="/internal/scheduler")


def get_db() -> Any:
    return get_database()


def get_now_fn() -> Callable[[], str]:
    return _utc_now_iso


def get_aerodatabox_client() -> Any:
    return _MissingProvider("AeroDataBox client")


def get_pubsub_publisher() -> Any:
    return _MissingProvider("Pub/Sub publisher")


def get_send_reminder_fn() -> Callable[[dict[str, Any]], dict[str, Any] | None]:
    def _missing(_: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("Reminder sender is not configured.")

    return _missing


@router.post("/reminders")
def run_reminder_scheduler_endpoint(
    db: Any = Depends(get_db),
    now_fn: Callable[[], str] = Depends(get_now_fn),
    send_reminder_fn: Callable[[dict[str, Any]], dict[str, Any] | None] = Depends(get_send_reminder_fn),
) -> dict[str, Any]:
    try:
        result = dispatch_due_reminders(db=db, now_iso=now_fn(), send_reminder_fn=send_reminder_fn)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"code": "SCHEDULER_PROVIDER_NOT_CONFIGURED", "message": str(exc)}) from exc
    return {"success": True, "result": result}


@router.post("/flights")
def run_flight_poll_scheduler_endpoint(
    db: Any = Depends(get_db),
    now_fn: Callable[[], str] = Depends(get_now_fn),
    aerodatabox_client: Any = Depends(get_aerodatabox_client),
    pubsub_publisher: Any = Depends(get_pubsub_publisher),
) -> dict[str, Any]:
    try:
        result = poll_active_trip_flights(
            db=db,
            now_iso=now_fn(),
            aerodatabox_client=aerodatabox_client,
            pubsub_publisher=pubsub_publisher,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"code": "SCHEDULER_PROVIDER_NOT_CONFIGURED", "message": str(exc)}) from exc
    return {"success": True, "result": result}


class _MissingProvider:
    def __init__(self, name: str):
        self.name = name

    def __getattr__(self, _: str) -> Any:
        raise RuntimeError(f"{self.name} is not configured.")


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
