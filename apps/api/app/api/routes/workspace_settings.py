from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.workspace_settings import WorkspaceSettingsRead, WorkspaceSettingsUpdate
from app.services.workspace_settings_service import read_workspace_settings, update_workspace_settings

router = APIRouter(prefix="/orgs/{organization_id}/workspace-settings", tags=["workspace-settings"])


@router.get("", response_model=WorkspaceSettingsRead)
def get_workspace_settings(organization_id: str, db: DbSession, current_user: CurrentUser):
    return read_workspace_settings(db, organization_id, current_user)


@router.patch("", response_model=WorkspaceSettingsRead)
def patch_workspace_settings(
    organization_id: str,
    payload: WorkspaceSettingsUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    return update_workspace_settings(db, organization_id, current_user, payload)