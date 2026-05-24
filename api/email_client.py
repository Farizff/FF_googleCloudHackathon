"""SendGrid email client — real and fake implementations.

get_email_client() returns the real client when SENDGRID_API_KEY is set,
otherwise a fake that prints to stdout so tests are observable.
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from sendgrid import SendGridAPIClient


class BaseEmailClient:
    """Shared interface for real and fake email clients."""

    def send_email(self, to_email: str, subject: str, body: str) -> dict[str, Any] | None:
        raise NotImplementedError


class RealSendGridClient(BaseEmailClient):
    """Send real transactional email via SendGrid v3 Web API."""

    def __init__(self, api_key: str, from_email: str):
        from sendgrid import SendGridAPIClient

        self._client: "SendGridAPIClient" = SendGridAPIClient(api_key)
        self._from_email = from_email

    def send_email(self, to_email: str, subject: str, body: str) -> dict[str, Any] | None:
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=self._from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body,
        )
        response = self._client.send(message)
        return {"message_id": response.headers.get("X-Message-Id", "")}


class FakeSendGridClient(BaseEmailClient):
    """Log every email to stdout; return a deterministic mock message_id for testing."""

    def __init__(self, from_email: str = "bounce@yourdomain.com"):
        self._from_email = from_email
        self._sent: list[dict[str, Any]] = []

    def send_email(self, to_email: str, subject: str, body: str) -> dict[str, Any] | None:
        msg_id = f"fake_msg_{len(self._sent) + 1}"
        entry = {
            "message_id": msg_id,
            "to_email": to_email,
            "subject": subject,
            "body": body,
        }
        self._sent.append(entry)
        print(f"[FakeSendGrid] 📧  TO: {to_email} | SUBJECT: {subject}", file=sys.stdout)
        return {"message_id": msg_id}

    @property
    def sent(self) -> list[dict[str, Any]]:
        """All messages logged by this fake client."""
        return self._sent


# Singleton instance (lazily created per process)
_email_client: BaseEmailClient | None = None


def get_email_client() -> BaseEmailClient:
    """Factory: real SendGrid client when SENDGRID_API_KEY is set, else fake."""
    global _email_client
    if _email_client is None:
        api_key = os.environ.get("SENDGRID_API_KEY", "").strip()
        if api_key:
            from api.settings import get_settings

            settings = get_settings()
            _email_client = RealSendGridClient(api_key, settings.sendgrid_from_email)
        else:
            _email_client = FakeSendGridClient()
    return _email_client


def reset_email_client() -> None:
    """Reset the singleton — intended for test isolation only."""
    global _email_client
    _email_client = None