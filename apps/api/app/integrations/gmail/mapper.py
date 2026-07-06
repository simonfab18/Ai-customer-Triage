import base64
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parseaddr, parsedate_to_datetime
from typing import Any


@dataclass(frozen=True)
class NormalizedGmailMessage:
    gmail_message_id: str
    gmail_thread_id: str | None
    customer_email: str
    customer_name: str | None
    subject: str
    message_text: str
    message_html: str | None
    received_at: datetime


def _headers_by_name(message: dict[str, Any]) -> dict[str, str]:
    headers = message.get("payload", {}).get("headers", [])
    return {header.get("name", "").lower(): header.get("value", "") for header in headers}


def _decode_body(data: str | None) -> str:
    if not data:
        return ""
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("utf-8")).decode("utf-8", errors="replace")


def _walk_parts(part: dict[str, Any]) -> list[dict[str, Any]]:
    parts = [part]
    for child in part.get("parts", []) or []:
        parts.extend(_walk_parts(child))
    return parts


def _body_for_mime(message: dict[str, Any], mime_type: str) -> str | None:
    payload = message.get("payload", {})
    for part in _walk_parts(payload):
        if part.get("mimeType") == mime_type:
            body = _decode_body(part.get("body", {}).get("data"))
            if body.strip():
                return body.strip()
    return None


def _received_at(headers: dict[str, str], internal_date: str | None) -> datetime:
    date_header = headers.get("date")
    if date_header:
        try:
            parsed = parsedate_to_datetime(date_header)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except (TypeError, ValueError):
            pass
    if internal_date:
        return datetime.fromtimestamp(int(internal_date) / 1000, tz=UTC)
    return datetime.now(UTC)


def normalize_gmail_message(message: dict[str, Any]) -> NormalizedGmailMessage:
    headers = _headers_by_name(message)
    sender_name, sender_email = parseaddr(headers.get("from", ""))
    message_text = _body_for_mime(message, "text/plain") or message.get("snippet") or ""
    message_html = _body_for_mime(message, "text/html")

    return NormalizedGmailMessage(
        gmail_message_id=message.get("id", ""),
        gmail_thread_id=message.get("threadId"),
        customer_email=sender_email or "unknown@example.local",
        customer_name=sender_name or None,
        subject=headers.get("subject") or "Customer support request",
        message_text=message_text.strip() or "No message body available.",
        message_html=message_html,
        received_at=_received_at(headers, message.get("internalDate")),
    )
