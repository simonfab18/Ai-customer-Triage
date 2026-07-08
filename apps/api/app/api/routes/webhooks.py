import base64
import json
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import DbSession
from app.models.gmail_connection import GmailConnection
from app.models.gmail_sync_event import GmailSyncEvent
from app.schemas.gmail import GmailWebhookAcceptedRead
from app.services.pubsub_verification_service import verify_pubsub_oidc_token

router = APIRouter(tags=["webhooks"])


class PubSubMessage(BaseModel):
    data: str | None = None
    message_id: str | None = Field(default=None, alias="messageId")
    publish_time: str | None = Field(default=None, alias="publishTime")
    attributes: dict[str, str] = Field(default_factory=dict)


class PubSubPushEnvelope(BaseModel):
    message: PubSubMessage
    subscription: str | None = None


def _decode_pubsub_payload(data: str | None) -> dict[str, Any]:
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pub/Sub message data is required")
    padded = data + "=" * (-len(data) % 4)
    try:
        decoded = base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
        payload = json.loads(decoded)
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pub/Sub message data is invalid") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pub/Sub message payload is invalid")
    return payload


@router.post("/webhooks/google/gmail", response_model=GmailWebhookAcceptedRead)
def google_gmail_webhook(
    envelope: PubSubPushEnvelope,
    db: DbSession,
    authorization: str | None = Header(default=None),
):
    verify_pubsub_oidc_token(authorization)
    payload = _decode_pubsub_payload(envelope.message.data)
    email_address = payload.get("emailAddress")
    history_id = str(payload.get("historyId") or "") or None
    message_id = envelope.message.message_id
    if not message_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pub/Sub messageId is required")
    if not email_address or not history_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gmail notification payload is incomplete")

    connection = db.scalar(
        select(GmailConnection).where(
            GmailConnection.gmail_email == email_address,
            GmailConnection.status == "active",
        )
    )
    if connection is None:
        return GmailWebhookAcceptedRead(status="accepted")

    now = datetime.now(UTC)
    connection.last_notification_at = now
    event = GmailSyncEvent(
        organization_id=connection.organization_id,
        gmail_connection_id=connection.id,
        trigger_type="pubsub_notification",
        status="received",
        pubsub_message_id=message_id,
        notification_history_id=history_id,
        sync_metadata={
            "gmail_email": email_address,
            "subscription": envelope.subscription,
            "delivery": "acknowledged_without_history_processing",
        },
        started_at=now,
        completed_at=now,
    )
    db.add(event)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
    return GmailWebhookAcceptedRead(status="accepted")
