from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketCategory, TicketPriority, TicketSentiment


class TriageOutput(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    sentiment: TicketSentiment
    summary: str = Field(min_length=1)
    suggested_action: str = Field(min_length=1)
    draft_reply: str = Field(min_length=1)
    confidence_score: int = Field(ge=0, le=100)
    reasoning: str = Field(min_length=1)
    requires_human_review: bool


class AITriageResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    ticket_id: str
    model_provider: str
    model_name: str
    category: str
    priority: str
    sentiment: str
    summary: str
    suggested_action: str
    draft_reply: str
    confidence_score: int
    reasoning: str
    requires_human_review: bool
    validation_status: str
    created_at: datetime
