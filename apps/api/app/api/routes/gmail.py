from fastapi import APIRouter, Request, Response, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.gmail import (
    GmailConnectionRead,
    GmailOAuthCallbackRead,
    GmailOAuthStartRead,
    GmailSyncEventRead,
    GmailWatchActionRead,
    MailImportRuleRead,
    MailImportRuleUpdate,
)
from app.services.gmail_connection_service import (
    complete_gmail_oauth,
    list_gmail_connections,
    list_import_rules,
    revoke_gmail_connection,
    start_gmail_oauth,
    update_import_rule,
)
from app.services.gmail_watch_service import list_sync_events, register_gmail_watch, renew_gmail_watch

router = APIRouter(tags=["gmail"])


@router.get(
    "/orgs/{organization_id}/gmail/oauth/start",
    response_model=GmailOAuthStartRead,
)
def start_oauth(organization_id: str, db: DbSession, current_user: CurrentUser):
    auth_url, state = start_gmail_oauth(db, organization_id, current_user)
    return GmailOAuthStartRead(auth_url=auth_url, state=state)


@router.get("/gmail/oauth/callback", response_model=GmailOAuthCallbackRead)
async def oauth_callback(state: str, code: str, request: Request, db: DbSession):
    connection = await complete_gmail_oauth(
        db,
        state,
        code,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return GmailOAuthCallbackRead(
        connection_id=connection.id,
        gmail_email=connection.gmail_email,
        status=connection.status,
    )


@router.get(
    "/orgs/{organization_id}/gmail/connections",
    response_model=list[GmailConnectionRead],
)
def read_connections(organization_id: str, db: DbSession, current_user: CurrentUser):
    return list_gmail_connections(db, organization_id, current_user)


@router.delete(
    "/orgs/{organization_id}/gmail/connections/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_connection(
    organization_id: str,
    connection_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    revoke_gmail_connection(db, organization_id, connection_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/orgs/{organization_id}/gmail/connections/{connection_id}/watch/register",
    response_model=GmailWatchActionRead,
)
async def register_watch(
    organization_id: str,
    connection_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    connection, event = await register_gmail_watch(db, organization_id, connection_id, current_user)
    return GmailWatchActionRead(connection=connection, event=event)


@router.post(
    "/orgs/{organization_id}/gmail/connections/{connection_id}/watch/renew",
    response_model=GmailWatchActionRead,
)
async def renew_watch(
    organization_id: str,
    connection_id: str,
    db: DbSession,
    current_user: CurrentUser,
):
    connection, event = await renew_gmail_watch(db, organization_id, connection_id, current_user)
    return GmailWatchActionRead(connection=connection, event=event)


@router.get(
    "/orgs/{organization_id}/gmail/sync-events",
    response_model=list[GmailSyncEventRead],
)
def read_sync_events(organization_id: str, db: DbSession, current_user: CurrentUser):
    return list_sync_events(db, organization_id, current_user)


@router.get(
    "/orgs/{organization_id}/gmail/import-rules",
    response_model=list[MailImportRuleRead],
)
def read_import_rules(organization_id: str, db: DbSession, current_user: CurrentUser):
    return list_import_rules(db, organization_id, current_user)


@router.patch(
    "/orgs/{organization_id}/gmail/import-rules/{rule_id}",
    response_model=MailImportRuleRead,
)
def patch_import_rule(
    organization_id: str,
    rule_id: str,
    payload: MailImportRuleUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    return update_import_rule(db, organization_id, rule_id, current_user, payload)
