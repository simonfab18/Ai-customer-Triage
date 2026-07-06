from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser
from app.models.ticket import Ticket, TicketStatus
from app.schemas.metrics import MetricsOverviewRead
from app.services.rbac_service import require_membership

ACTIVE_STATUSES = {
    TicketStatus.NEW.value,
    TicketStatus.OPEN.value,
    TicketStatus.PENDING.value,
    TicketStatus.DRAFT_CREATED.value,
}


def get_metrics_overview(db: Session, organization_id: str, actor: AuthenticatedUser) -> MetricsOverviewRead:
    require_membership(db, organization_id, actor)

    status_rows = db.execute(
        select(Ticket.status, func.count(Ticket.id))
        .where(Ticket.organization_id == organization_id)
        .group_by(Ticket.status)
    ).all()
    priority_rows = db.execute(
        select(Ticket.priority, func.count(Ticket.id))
        .where(Ticket.organization_id == organization_id)
        .group_by(Ticket.priority)
    ).all()

    by_status = {status: count for status, count in status_rows}
    by_priority = {priority: count for priority, count in priority_rows}

    return MetricsOverviewRead(
        total_tickets=sum(by_status.values()),
        active_tickets=sum(by_status.get(status, 0) for status in ACTIVE_STATUSES),
        resolved_tickets=by_status.get(TicketStatus.RESOLVED.value, 0),
        spam_tickets=by_status.get(TicketStatus.SPAM.value, 0),
        critical_tickets=by_priority.get("critical", 0),
        high_priority_tickets=by_priority.get("high", 0),
        draft_created_tickets=by_status.get(TicketStatus.DRAFT_CREATED.value, 0),
        by_status=by_status,
        by_priority=by_priority,
    )