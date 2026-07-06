from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.audit_log import AuditLogRead
from app.services.audit_log_service import list_audit_logs

router = APIRouter(tags=["audit-logs"])


@router.get("/orgs/{organization_id}/audit-logs", response_model=list[AuditLogRead])
def read_audit_logs(organization_id: str, db: DbSession, current_user: CurrentUser):
    return list_audit_logs(db, organization_id, current_user)