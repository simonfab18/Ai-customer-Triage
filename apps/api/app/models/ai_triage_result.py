from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class AITriageResult(Base):
    __tablename__ = "ai_triage_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id"), nullable=False, index=True)
    model_provider: Mapped[str] = mapped_column(String(80), nullable=False, default="google")
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    raw_input: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    raw_output: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    validated_output: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_action: Mapped[str] = mapped_column(Text, nullable=False)
    draft_reply: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[int] = mapped_column(default=0, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, default="", nullable=False)
    requires_human_review: Mapped[bool] = mapped_column(Boolean, nullable=False)
    validation_status: Mapped[str] = mapped_column(String(20), nullable=False, default="valid")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
