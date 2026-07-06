from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser
from app.models.member import MemberRole
from app.models.workspace_settings import WorkspaceSettings
from app.schemas.workspace_settings import WorkspaceSettingsUpdate
from app.services.rbac_service import require_membership, require_role


def get_or_create_workspace_settings(db: Session, organization_id: str) -> WorkspaceSettings:
    settings = db.scalar(
        select(WorkspaceSettings).where(WorkspaceSettings.organization_id == organization_id)
    )
    if settings is not None:
        return settings

    settings = WorkspaceSettings(organization_id=organization_id)
    db.add(settings)
    db.flush()
    return settings


def read_workspace_settings(
    db: Session,
    organization_id: str,
    actor: AuthenticatedUser,
) -> WorkspaceSettings:
    require_membership(db, organization_id, actor)
    settings = get_or_create_workspace_settings(db, organization_id)
    db.commit()
    db.refresh(settings)
    return settings


def update_workspace_settings(
    db: Session,
    organization_id: str,
    actor: AuthenticatedUser,
    payload: WorkspaceSettingsUpdate,
) -> WorkspaceSettings:
    require_role(db, organization_id, actor, {MemberRole.OWNER, MemberRole.ADMIN})
    settings = get_or_create_workspace_settings(db, organization_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings