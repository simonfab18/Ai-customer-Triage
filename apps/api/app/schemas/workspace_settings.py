from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    default_reply_signature: str
    auto_triage_enabled: bool
    draft_requires_approval: bool
    sync_enabled: bool
    draft_creation_enabled: bool
    pilot_feedback_contact: str | None
    created_at: datetime
    updated_at: datetime


class WorkspaceSettingsUpdate(BaseModel):
    default_reply_signature: str | None = Field(default=None, min_length=1)
    auto_triage_enabled: bool | None = None
    draft_requires_approval: bool | None = None
    sync_enabled: bool | None = None
    draft_creation_enabled: bool | None = None
    pilot_feedback_contact: str | None = Field(default=None, max_length=255)
