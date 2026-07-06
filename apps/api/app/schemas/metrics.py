from pydantic import BaseModel


class MetricsOverviewRead(BaseModel):
    total_tickets: int
    active_tickets: int
    resolved_tickets: int
    spam_tickets: int
    critical_tickets: int
    high_priority_tickets: int
    draft_created_tickets: int
    by_status: dict[str, int]
    by_priority: dict[str, int]