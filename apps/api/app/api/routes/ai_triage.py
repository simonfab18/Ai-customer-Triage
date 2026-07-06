from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.ai import AITriageResultRead
from app.services.ai_triage_service import list_ticket_triage_results, run_ticket_triage

router = APIRouter(tags=["ai-triage"])


@router.post(
    "/orgs/{organization_id}/tickets/{ticket_id}/triage",
    response_model=AITriageResultRead,
    status_code=status.HTTP_201_CREATED,
)
async def triage_ticket(
    organization_id: str,
    ticket_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    return await run_ticket_triage(db, organization_id, ticket_id, current_user)


@router.get("/orgs/{organization_id}/tickets/{ticket_id}/triage", response_model=list[AITriageResultRead])
def read_ticket_triage_results(
    organization_id: str,
    ticket_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    return list_ticket_triage_results(db, organization_id, ticket_id, current_user)


@router.get("/orgs/{organization_id}/tickets/{ticket_id}/triage-results", response_model=list[AITriageResultRead])
def read_ticket_triage_results_alias(
    organization_id: str,
    ticket_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    return list_ticket_triage_results(db, organization_id, ticket_id, current_user)