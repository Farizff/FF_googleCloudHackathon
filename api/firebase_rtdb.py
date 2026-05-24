from __future__ import annotations

from typing import Any, Callable
from urllib.parse import quote

import httpx


class FirebaseProviderNotConfigured(RuntimeError):
    """Raised when Firebase RTDB is required but no database URL is configured."""


class FirebasePublishError(RuntimeError):
    """Raised when a Firebase RTDB REST write fails."""


RequestJsonFn = Callable[[str, str, dict[str, Any]], Any]


class FirebaseRtdbPublisher:
    """Small REST publisher for Bounce Firebase Realtime Database demo paths.

    Uses the RTDB REST API so local tests can inject a tiny requester and Cloud
    Run can publish to the demo database configured by BNC-018.
    """

    def __init__(self, database_url: str, request_json: RequestJsonFn | None = None):
        normalized_url = database_url.strip().rstrip("/")
        if not normalized_url:
            raise FirebaseProviderNotConfigured("FIREBASE_DATABASE_URL is not configured.")
        self.database_url = normalized_url
        self.request_json = request_json or _request_json

    def publish_main_thread_message(self, *, trip_id: str, author_id: str, text: str, role: str, message_id: str) -> str:
        path = f"/trips/{trip_id}/threads/main/{message_id}"
        self._put(
            path,
            {
                "message_id": message_id,
                "author_id": author_id,
                "role": role,
                "text": text,
            },
        )
        return path

    def broadcast_itinerary_update(self, trip_id: str, payload: dict[str, Any]) -> None:
        self._patch(f"/trips/{trip_id}/state/itinerary", payload)

    def broadcast_group_state(self, trip_id: str, payload: dict[str, Any]) -> None:
        self._patch(f"/trips/{trip_id}/state/group", payload)

    def _put(self, path: str, payload: dict[str, Any]) -> Any:
        return self.request_json("PUT", self._url_for(path), payload)

    def _patch(self, path: str, payload: dict[str, Any]) -> Any:
        return self.request_json("PATCH", self._url_for(path), payload)

    def _url_for(self, path: str) -> str:
        encoded_path = "/".join(quote(part, safe="") for part in path.strip("/").split("/"))
        return f"{self.database_url}/{encoded_path}.json"


def _request_json(method: str, url: str, payload: dict[str, Any]) -> Any:
    try:
        response = httpx.request(method, url, json=payload, timeout=10)
        response.raise_for_status()
    except httpx.HTTPError as exc:  # pragma: no cover - live network path
        raise FirebasePublishError(f"Firebase RTDB write failed: {exc}") from exc
    if not response.content:
        return None
    return response.json()
