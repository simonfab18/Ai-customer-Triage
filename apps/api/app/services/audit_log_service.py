from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser
from app.models.audit_log import AuditLog
from app.services.rbac_service import require_membership

SENSITIVE_KEY_PARTS = (
    "token",
    "secret",
    "password",
    "authorization",
    "api_key",
    "apikey",
    "refresh",
    "access",
)
REDACTED = "[REDACTED]"


def redact_sensitive_values(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                redacted[key] = REDACTED
            else:
                redacted[key] = redact_sensitive_values(item)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive_values(item) for item in value]
    return value


def create_audit_log(
    db: Session,
    organization_id: str,
    actor_user_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        audit_metadata=redact_sensitive_values(metadata or {}),
    )
    db.add(audit_log)
    return audit_log


def list_audit_logs(db: Session, organization_id: str, actor: AuthenticatedUser) -> list[AuditLog]:
    require_membership(db, organization_id, actor)
    return list(
        db.scalars(
            select(AuditLog)
            .where(AuditLog.organization_id == organization_id)
            .order_by(AuditLog.created_at.desc())
        )
    )