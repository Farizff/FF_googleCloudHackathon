import re
from collections import defaultdict
from dataclasses import dataclass
from time import time
from typing import Callable
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

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
    """Small deterministic planning seam until Agent Builder is wired live."""

    def plan(self, request: ChatRequest) -> PlanningResult:
        trip_id = request.trip_id or f"trip_draft_{request.user_id}"
        intent = classify_intent(request.message)
        message = build_planning_message(request.message, intent)
        return PlanningResult(
            message=message,
            intent=intent,
            trip_id=trip_id,
            actions=["classify_intent", "start_planning_response"],
        )


class NoopChatPublisher:
    """Firebase-compatible path publisher seam for tests and blocked live RTDB."""

    def publish_main_thread_message(self, *, trip_id: str, author_id: str, text: str, role: str, message_id: str) -> str:
        return f"/trips/{trip_id}/threads/main/{message_id}"


def get_time_fn() -> Callable[[], float]:
    return time


def get_planner() -> LocalPlanningOrchestrator:
    return LocalPlanningOrchestrator()


def get_chat_publisher() -> NoopChatPublisher:
    return NoopChatPublisher()


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    planner: LocalPlanningOrchestrator = Depends(get_planner),
    publisher: NoopChatPublisher = Depends(get_chat_publisher),
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
    path = publisher.publish_main_thread_message(
        trip_id=result.trip_id,
        author_id="bounce",
        text=result.message,
        role="assistant",
        message_id=message_id,
    )

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
