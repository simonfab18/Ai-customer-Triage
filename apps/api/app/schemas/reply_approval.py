from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.reply_suggestion import ReplySuggestionRead


class ReplyApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    ticket_id: str
    ai_triage_result_id: str
    gmail_connection_id: str | None = None
    suggested_reply: str
    final_reply: str | None = None
    status: str
    reply_version: int
    approved_reply_version: int | None = None
    approved_by_user_id: str | None = None
    approved_at: datetime | None = None
    gmail_draft_id: str | None = None
    created_at: datetime
    updated_at: datetime


class ReplyApprovalUpdate(BaseModel):
    final_reply: str = Field(min_length=1)


class GmailDraftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    ticket_id: str
    reply_suggestion_id: str
    gmail_draft_id: str
    gmail_thread_id: str | None = None
    created_by_user_id: str
    created_at: datetime


class GmailDraftCreateRead(BaseModel):
    approval: ReplyApprovalRead | ReplySuggestionRead
    draft: GmailDraftRead
    gmail_draft_id: str
