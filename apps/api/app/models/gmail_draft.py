from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class GmailDraft(Base):
    __tablename__ = "gmail_drafts"
    __table_args__ = (UniqueConstraint("organization_id", "reply_suggestion_id", name="uq_gmail_draft_org_suggestion"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id"), nullable=False, index=True)
    reply_suggestion_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    gmail_draft_id: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    gmail_thread_id: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    created_by_user_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
