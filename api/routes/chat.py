import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from time import time
from typing import Callable
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.firebase_rtdb import FirebaseProviderNotConfigured, FirebasePublishError, FirebaseRtdbPublisher
from api.routes import trip as trip_module
from api.settings import get_settings

router = APIRouter()

PII_PATTERNS = {
    "passport_number": re.compile(r"[A-Z]{1,2}\d{6,9}"),
    "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
    "ssn_us": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "national_id_id": re.compile(r"\b\d{12,16}\b"),
}

PII_RESPONSE = "Heads up — I don't need or store that. Let's continue without it."
RATE_LIMIT_RESPONSE = "Please slow down — Bounce chat allows 5 messages every 10 seconds per user."
PLANNER_UNAVAILABLE_RESPONSE = "I can’t reach the planning brain right now. Please try again in a moment."
LOADING_STATES = [
    "reading_group_context",
    "classifying_intent",
    "planning_next_step",
    "publishing_response",
]

rate_buckets: defaultdict[str, list[float]] = defaultdict(list)


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=4000)
    trip_id: str | None = None
    role: str = "member"


class ChatResponse(BaseModel):
    success: bool
    message: str
    intent: str
    trip_id: str
    planning_response_path: str
    loading_states: list[str]
    actions: list[str]


@dataclass(frozen=True)
class PlanningResult:
    message: str
    intent: str
    trip_id: str
    actions: list[str]


class PlanningError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class LocalPlanningOrchestrator:
    """Planning seam that extracts trip details and optionally creates a real trip document."""

    def plan(self, request: ChatRequest) -> PlanningResult:
        intent = classify_intent(request.message)

        # If trip_id already provided, use it without creating a new trip
        if request.trip_id:
            trip_id = request.trip_id
            message = build_planning_message(request.message, intent)
            return PlanningResult(
                message=message,
                intent=intent,
                trip_id=trip_id,
                actions=["classify_intent", "start_planning_response"],
            )

        # Otherwise, extract destination/date/people from message and create a real trip
        extracted = extract_trip_fields(request.user_id, request.message)
        created = create_trip_from_extraction(
            user_id=request.user_id,
            name=extracted.get("name", request.user_id),
            destination_city=extracted.get("destination_city", "Unknown"),
            destination_country=extracted.get("destination_country", "Unknown"),
            destination_iata=extracted.get("destination_iata", "SYD"),
            departure_date=extracted.get("departure_date"),
            return_date=extracted.get("return_date"),
            num_people=extracted.get("num_people"),
            occasion=extracted.get("occasion"),
            origin_city_iata=extracted.get("origin_city_iata"),
        )
        trip_id = created["trip_id"]

        message = build_planning_message(request.message, intent)
        return PlanningResult(
            message=message,
            intent=intent,
            trip_id=trip_id,
            actions=["extract_trip_fields", "create_trip", "start_planning_response"],
        )


def extract_trip_fields(user_id: str, message: str) -> dict:
    """Extract trip parameters from natural language message."""
    normalized = message.lower()
    fields: dict = {"name": user_id}

    # Destination city - simple keyword mapping
    destinations = {
        "tokyo": ("Tokyo", "Japan", "NRT"),
        "paris": ("Paris", "France", "CDG"),
        "london": ("London", "UK", "LHR"),
        "new york": ("New York", "USA", "JFK"),
        "sydney": ("Sydney", "Australia", "SYD"),
        "singapore": ("Singapore", "Singapore", "SIN"),
        "dubai": ("Dubai", "UAE", "DXB"),
        "rome": ("Rome", "Italy", "FCO"),
        "barcelona": ("Barcelona", "Spain", "BCN"),
        "bali": ("Bali", "Indonesia", "DPS"),
        "lisbon": ("Lisbon", "Portugal", "LIS"),
        "berlin": ("Berlin", "Germany", "BER"),
        "amsterdam": ("Amsterdam", "Netherlands", "AMS"),
        "miami": ("Miami", "USA", "MIA"),
        "los angeles": ("Los Angeles", "USA", "LAX"),
        "san francisco": ("San Francisco", "USA", "SFO"),
        "chicago": ("Chicago", "USA", "ORD"),
        "boston": ("Boston", "USA", "BOS"),
        "seattle": ("Seattle", "USA", "SEA"),
        "denver": ("Denver", "USA", "DEN"),
        "phoenix": ("Phoenix", "USA", "PHX"),
        "las vegas": ("Las Vegas", "USA", "LAS"),
        "honolulu": ("Honolulu", "USA", "HNL"),
        "maui": ("Maui", "USA", "OGG"),
        "toronto": ("Toronto", "Canada", "YYZ"),
        "vancouver": ("Vancouver", "Canada", "YVR"),
        "mexico city": ("Mexico City", "Mexico", "MEX"),
        "cancun": ("Cancun", "Mexico", "CUN"),
        "buenos aires": ("Buenos Aires", "Argentina", "EZE"),
        "rio de janeiro": ("Rio de Janeiro", "Brazil", "GIG"),
        "são paulo": ("São Paulo", "Brazil", "GRU"),
        "hong kong": ("Hong Kong", "China", "HKG"),
        "shanghai": ("Shanghai", "China", "PVG"),
        "beijing": ("Beijing", "China", "PEK"),
        "seoul": ("Seoul", "South Korea", "ICN"),
        "bangkok": ("Bangkok", "Thailand", "BKK"),
        "phuket": ("Phuket", "Thailand", "HKT"),
        "kuala lumpur": ("Kuala Lumpur", "Malaysia", "KUL"),
        "manila": ("Manila", "Philippines", "MNL"),
        "mumbai": ("Mumbai", "India", "BOM"),
        "delhi": ("Delhi", "India", "DEL"),
        "bangalore": ("Bangalore", "India", "BLR"),
        "tokyo": ("Tokyo", "Japan", "NRT"),
        "osaka": ("Osaka", "Japan", "KIX"),
        "kyoto": ("Kyoto", "Japan", "KIX"),
        "sapporo": ("Sapporo", "Japan", "CTS"),
    }

    for key, (city, country, iata) in destinations.items():
        if key in normalized:
            fields["destination_city"] = city
            fields["destination_country"] = country
            fields["destination_iata"] = iata
            break

    # Number of people - look for patterns like "for 10 friends", "for 4 people"
    people_match = re.search(r"(?:for|of)\s+(\d+)\s+(?:people|friends|travelers|pax)", normalized)
    if people_match:
        fields["num_people"] = int(people_match.group(1))

    # Dates - look for month names and day patterns
    month_map = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12",
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "jun": "06", "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    }
    date_match = re.search(r"(july|august|september|october|january|february|march|april|may|june|november|december)", normalized)
    if date_match:
        month = month_map[date_match.group(1)]
        day_match = re.search(r"(\d{1,2})(?:st|nd|rd|th)?", normalized)
        if day_match:
            day = day_match.group(1).zfill(2)
            fields["departure_date"] = f"2026-{month}-{day}"

    # Trip duration - "7 day", "5-night"
    duration_match = re.search(r"(\d+)\s*(?:day|night|days|nights)", normalized)
    if duration_match:
        duration = int(duration_match.group(1))
        if "night" in normalized or "days" not in normalized:
            # e.g., "7-night" or "7 nights"
            fields["num_nights"] = duration
        else:
            fields["num_days"] = duration

    # Occasion detection
    occasions = {
        "reunion": "reunion",
        "birthday": "birthday",
        "anniversary": "anniversary",
        "honeymoon": "honeymoon",
        "wedding": "wedding",
        "graduation": "graduation",
        "conference": "conference",
        "team offsite": "corporate offsite",
        "offsite": "corporate offsite",
        "vacation": "vacation",
        "holiday": "holiday",
    }
    for keyword, occasion in occasions.items():
        if keyword in normalized:
            fields["occasion"] = occasion
            break

    return fields


def create_trip_from_extraction(
    user_id: str,
    name: str,
    destination_city: str,
    destination_country: str = "Unknown",
    destination_iata: str = "SYD",
    departure_date: str | None = None,
    return_date: str | None = None,
    num_people: int | None = None,
    occasion: str | None = None,
    origin_city_iata: str | None = None,
) -> dict:
    """Call POST /trips/simple internally to create a real trip document."""
    db = trip_module.get_db()
    id_fn = trip_module.get_id_fn()
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    trip_id = id_fn("trip")

    group_type = "friends"
    trip_mode = "international"

    trip = {
        "trip_id": trip_id,
        "created_at": now,
        "invite_token": id_fn("invite"),
        "group_type": group_type,
        "trip_mode": trip_mode,
        "status": "planning",
        "special_occasion": occasion,
        "destination_city": destination_city,
        "destination_country": destination_country,
        "destination_iata": destination_iata,
        "departure_date": departure_date,
        "return_date": return_date,
        "members": [
            {
                "user_id": user_id,
                "name": name,
                "role": "organiser",
                "origin_city_iata": origin_city_iata,
                "joined_at": now,
                "profile_complete": False,
                "shares_compliance_with_admins": True,
            }
        ],
        "contacts": [],
        "office_details": {"company_name": None, "cost_centre": None},
        "shared_budget_estimate_usd": 0,
        "all_members_budget_ok": False,
        "jet_lag_override": False,
    }
    db.group_trips.insert_one(trip)
    trip_module._insert_invite_token(db, token=trip["invite_token"], trip_id=trip_id)
    return {"success": True, "trip_id": trip_id, "trip": trip}


def get_time_fn() -> Callable[[], float]:
    return time


def get_planner() -> LocalPlanningOrchestrator:
    return LocalPlanningOrchestrator()


def get_chat_publisher() -> FirebaseRtdbPublisher:
    settings = get_settings()
    return FirebaseRtdbPublisher(settings.firebase_database_url)


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    planner: LocalPlanningOrchestrator = Depends(get_planner),
    publisher: FirebaseRtdbPublisher = Depends(get_chat_publisher),
    time_fn: Callable[[], float] = Depends(get_time_fn),
) -> ChatResponse:
    pii_detected, pii_type = check_for_pii(request.message)
    if pii_detected:
        raise HTTPException(
            status_code=400,
            detail={"code": "PII_DETECTED", "pii_type": pii_type, "message": PII_RESPONSE},
        )

    if not check_rate(request.user_id, now=time_fn()):
        raise HTTPException(
            status_code=429,
            detail={"code": "RATE_LIMITED", "message": RATE_LIMIT_RESPONSE},
        )

    try:
        result = planner.plan(request)
    except PlanningError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": exc.code, "message": PLANNER_UNAVAILABLE_RESPONSE},
        ) from exc

    message_id = f"msg_{uuid4().hex}"
    try:
        path = publisher.publish_main_thread_message(
            trip_id=result.trip_id,
            author_id="bounce",
            text=result.message,
            role="assistant",
            message_id=message_id,
        )
    except FirebaseProviderNotConfigured as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "FIREBASE_PROVIDER_NOT_CONFIGURED", "message": "Firebase Realtime Database is not configured."},
        ) from exc
    except FirebasePublishError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "FIREBASE_PUBLISH_FAILED", "message": "Firebase Realtime Database publish failed."},
        ) from exc

    return ChatResponse(
        success=True,
        message=result.message,
        intent=result.intent,
        trip_id=result.trip_id,
        planning_response_path=path,
        loading_states=LOADING_STATES,
        actions=result.actions,
    )


def check_for_pii(message: str) -> tuple[bool, str | None]:
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(message):
            return True, pii_type
    return False, None


def check_rate(user_id: str, now: float | None = None) -> bool:
    current_time = time() if now is None else now
    rate_buckets[user_id] = [timestamp for timestamp in rate_buckets[user_id] if current_time - timestamp < 10]
    if len(rate_buckets[user_id]) >= 5:
        return False
    rate_buckets[user_id].append(current_time)
    return True


def classify_intent(message: str) -> str:
    normalized = message.lower()
    if any(keyword in normalized for keyword in ["plan", "trip", "itinerary", "days", "reunion"]):
        return "full_trip_planning"
    if any(keyword in normalized for keyword in ["slower", "remove", "add", "change"]):
        return "partial_change"
    if any(keyword in normalized for keyword in ["budget", "afford", "cost"]):
        return "budget_question"
    return "information_query"


def build_planning_message(message: str, intent: str) -> str:
    if intent == "full_trip_planning":
        return "I can help plan that trip. I’ll start with the group basics, then shape the first itinerary path."
    if intent == "partial_change":
        return "Got it — I’ll treat that as a focused change and only touch the affected part of the plan."
    if intent == "budget_question":
        return "I’ll check the budget impact before suggesting a change."
    return "I can help with that."
