from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.ticket import (
    TicketAssign,
    TicketCreate,
    TicketEventRead,
    TicketListItem,
    TicketRead,
    TicketUpdate,
)
from app.services.ticket_service import (
    assign_ticket,
    create_ticket,
    get_ticket_or_404,
    list_ticket_events,
    list_tickets,
    mark_ticket_spam,
    resolve_ticket,
    update_ticket,
)

router = APIRouter(prefix="/orgs/{organization_id}/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketListItem])
def read_tickets(
    organization_id: str,
    db: DbSession,
    current_user: CurrentUser,
    status_filter: str | None = Query(default=None, alias="status"),
    priority_filter: str | None = Query(default=None, alias="priority"),
):
    return list_tickets(db, organization_id, current_user, status_filter, priority_filter)


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_org_ticket(
    organization_id: str,
    payload: TicketCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    return create_ticket(db, organization_id, current_user, payload)


@router.get("/{ticket_id}", response_model=TicketRead)
def read_ticket(organization_id: str, ticket_id: str, db: DbSession, current_user: CurrentUser):
    return get_ticket_or_404(db, organization_id, ticket_id, current_user)


@router.patch("/{ticket_id}", response_model=TicketRead)
def update_org_ticket(
    organization_id: str,
    ticket_id: str,
    payload: TicketUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    return update_ticket(db, organization_id, ticket_id, current_user, payload)


@router.post("/{ticket_id}/assign", response_model=TicketRead)
def assign_org_ticket(
    organization_id: str,
    ticket_id: str,
    payload: TicketAssign,
    db: DbSession,
    current_user: CurrentUser,
):
    return assign_ticket(db, organization_id, ticket_id, current_user, payload)


@router.post("/{ticket_id}/mark-spam", response_model=TicketRead)
def mark_org_ticket_spam(
    organization_id: str,
    ticket_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    return mark_ticket_spam(db, organization_id, ticket_id, current_user)


@router.post("/{ticket_id}/resolve", response_model=TicketRead)
def resolve_org_ticket(
    organization_id: str,
    ticket_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    return resolve_ticket(db, organization_id, ticket_id, current_user)


@router.get("/{ticket_id}/events", response_model=list[TicketEventRead])
def read_ticket_events(
    organization_id: str,
    ticket_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    return list_ticket_events(db, organization_id, ticket_id, current_user)
