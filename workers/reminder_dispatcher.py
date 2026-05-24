from typing import Any, Callable


def dispatch_due_reminders(
    db: Any,
    now_iso: str,
    send_reminder_fn: Callable[[dict[str, Any]], dict[str, Any] | None],
) -> dict[str, int]:
    """Send private due reminders once and record notification_log entries.

    The worker is intentionally dependency-injected so Cloud Scheduler, tests, and
    local scripts can run the same deterministic logic without live SendGrid.
    """
    reminders = list(db.compliance_reminders.find({}))
    result = {"scanned": len(reminders), "sent": 0, "skipped": 0, "failed": 0}

    for reminder in reminders:
        if not _is_due_unsent(reminder, now_iso):
            result["skipped"] += 1
            continue

        try:
            response = send_reminder_fn(reminder) or {}
            db.compliance_reminders.update_one(
                _reminder_query(reminder),
                {"$set": {"sent_at": now_iso, "send_status": "sent"}},
            )
            db.notification_log.insert_one(
                {
                    "trip_id": reminder.get("trip_id"),
                    "user_id": reminder.get("user_id"),
                    "trigger_event": "compliance_reminder",
                    "status": "sent",
                    "visibility": reminder.get("visibility", "private_to_member"),
                    "sent_at": now_iso,
                    "message": reminder.get("message"),
                    **({"message_id": response["message_id"]} if response.get("message_id") else {}),
                }
            )
            result["sent"] += 1
        except Exception as exc:  # pragma: no cover - failure path is deterministic but provider-specific
            db.notification_log.insert_one(
                {
                    "trip_id": reminder.get("trip_id"),
                    "user_id": reminder.get("user_id"),
                    "trigger_event": "compliance_reminder",
                    "status": "failed",
                    "visibility": reminder.get("visibility", "private_to_member"),
                    "sent_at": now_iso,
                    "error": str(exc),
                }
            )
            result["failed"] += 1

    return result


def _is_due_unsent(reminder: dict[str, Any], now_iso: str) -> bool:
    due_at = reminder.get("due_at")
    return bool(due_at and due_at <= now_iso and not reminder.get("sent_at"))


def _reminder_query(reminder: dict[str, Any]) -> dict[str, Any]:
    if reminder.get("reminder_id"):
        return {"reminder_id": reminder["reminder_id"]}
    return {
        "trip_id": reminder.get("trip_id"),
        "user_id": reminder.get("user_id"),
        "destination_iso": reminder.get("destination_iso"),
    }
