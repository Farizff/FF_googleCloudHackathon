from datetime import UTC, datetime
from typing import Any, Callable


ENGLISH_CODES = {"", "en", "eng", "english"}


def notify_contacts(
    trip_id: str,
    trigger_event: str,
    notification_context: dict[str, Any],
    contacts_collection: Any,
    notification_log_collection: Any,
    send_email_fn: Callable[[str, str, str], dict[str, Any] | None],
    translate_fn: Callable[[str, str], str] | None = None,
    clock: Callable[[], str] | None = None,
) -> dict[str, int]:
    """Notify trip contacts via injected email/translation dependencies."""
    sent_at = (clock or _utc_now_iso)()
    contacts = list(contacts_collection.find({"trip_id": trip_id}))
    sent = 0
    failed = 0

    for contact in contacts:
        email = contact.get("email")
        subject = f"Bounce trip update: {trigger_event.replace('_', ' ')}"
        body = _build_body(contact.get("detail_level", "summary"), notification_context)
        language = str(contact.get("language") or contact.get("preferred_language") or "en").lower()
        if translate_fn is not None and language not in ENGLISH_CODES:
            body = translate_fn(body, language)

        try:
            response = send_email_fn(email, subject, body) or {}
            sent += 1
            log_document = {
                "trip_id": trip_id,
                "email": email,
                "trigger_event": trigger_event,
                "status": "sent",
                "sent_at": sent_at,
            }
            if response.get("message_id"):
                log_document["message_id"] = response["message_id"]
            notification_log_collection.insert_one(log_document)
        except Exception as exc:  # pragma: no cover - exercised by tests, branch kept explicit
            failed += 1
            notification_log_collection.insert_one(
                {
                    "trip_id": trip_id,
                    "email": email,
                    "trigger_event": trigger_event,
                    "status": "failed",
                    "sent_at": sent_at,
                    "error": str(exc),
                }
            )

    return {"sent": sent, "failed": failed}


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _build_body(detail_level: str, context: dict[str, Any]) -> str:
    changes_summary = str(context.get("changes_summary") or "Trip details updated.")
    event_description = str(context.get("event_description") or "A trip update is available.")
    normalized = str(detail_level or "summary").lower()

    if normalized == "full":
        return (
            f"Bounce trip update\n"
            f"What happened: {event_description}\n"
            f"What changed: {changes_summary}\n"
            "Open Bounce for the latest itinerary."
        )
    if normalized == "updates_only":
        return f"Bounce update: {changes_summary}"
    return f"Bounce trip update\nWhat changed: {changes_summary}"
