from datetime import date, datetime
from typing import Any, Callable


VISA_REQUIREMENTS_UNAVAILABLE = "VISA_REQUIREMENTS_UNAVAILABLE"
VERIFY_NOTE = "Verify with the embassy — requirements may change."
REQUIRED_FIELDS = {
    "passport_iso",
    "destination_iso",
    "visa_required",
    "visa_type",
    "processing_days_min",
    "processing_days_max",
    "official_url",
    "fee_usd_estimate",
    "notes",
}


def get_visa_requirements(
    passport_iso: str,
    destination_iso: str,
    visa_requirements_collection: Any,
    web_search_fn: Callable[[str, str], dict[str, Any] | None] | None = None,
    clock: Callable[[], str] | None = None,
) -> dict[str, Any]:
    """Return visa requirements from cache, falling back to an injected web search."""
    today = _parse_date((clock or _today_iso)()) or date.today()
    passport = _normalize_iso(passport_iso)
    destination = _normalize_iso(destination_iso)
    query = {"passport_iso": passport, "destination_iso": destination}

    cached = visa_requirements_collection.find_one(query)
    if cached and _is_fresh(cached.get("last_verified"), today):
        return {**_with_verify_note(cached), "source": "mongo"}

    if web_search_fn is None:
        return _unavailable(passport, destination)

    fallback = web_search_fn(passport, destination)
    if not _is_valid_document(fallback):
        return _unavailable(passport, destination)

    result = _with_verify_note(
        {
            **fallback,
            "passport_iso": passport,
            "destination_iso": destination,
            "last_verified": today.isoformat(),
            "cache_ttl_days": 30,
        }
    )
    visa_requirements_collection.update_one(query, {"$set": result}, upsert=True)
    return {**result, "source": "fallback"}


def _today_iso() -> str:
    return date.today().isoformat()


def _normalize_iso(value: str) -> str:
    return str(value or "").strip().upper()


def _parse_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.strip().replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None


def _is_fresh(last_verified: Any, today: date) -> bool:
    verified = _parse_date(last_verified)
    if verified is None:
        return False
    return (today - verified).days <= 90


def _with_verify_note(document: dict[str, Any]) -> dict[str, Any]:
    result = dict(document)
    notes = str(result.get("notes") or "").strip()
    if VERIFY_NOTE.lower() not in notes.lower():
        result["notes"] = f"{notes} {VERIFY_NOTE}".strip()
    else:
        result["notes"] = notes
    return result


def _is_valid_document(document: Any) -> bool:
    if not isinstance(document, dict):
        return False
    return REQUIRED_FIELDS.issubset(document.keys())


def _unavailable(passport_iso: str, destination_iso: str) -> dict[str, dict[str, str]]:
    return {
        "error": {
            "code": VISA_REQUIREMENTS_UNAVAILABLE,
            "message": f"Visa requirements unavailable for {passport_iso} to {destination_iso}.",
        }
    }
