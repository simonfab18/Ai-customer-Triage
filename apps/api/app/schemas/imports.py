from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GmailSyncRequest(BaseModel):
    max_results: int = Field(default=20, ge=1, le=100)


class JobRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    job_type: str
    status: str
    error_message: str | None = None
    job_metadata: dict
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime
