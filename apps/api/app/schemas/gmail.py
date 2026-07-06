from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GmailOAuthStartRead(BaseModel):
    auth_url: str
    state: str


class GmailOAuthCallbackRead(BaseModel):
    connection_id: str
    gmail_email: str
    status: str


class GmailConnectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    connected_by_user_id: str
    gmail_email: str
    google_account_id: str
    scopes: str
    status: str
    last_sync_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class MailImportRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    gmail_connection_id: str
    support_label_id: str | None = None
    processed_label_id: str | None = None
    spam_label_id: str | None = None
    import_unread_only: bool
    is_active: bool
    created_at: datetime


class MailImportRuleUpdate(BaseModel):
    support_label_id: str | None = None
    processed_label_id: str | None = None
    spam_label_id: str | None = None
    import_unread_only: bool | None = None
    is_active: bool | None = None
