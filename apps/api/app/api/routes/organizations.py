from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.organization import OrganizationCreate, OrganizationRead
from app.services.organization_service import create_organization, get_organization
from app.services.rbac_service import require_membership

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_org(payload: OrganizationCreate, db: DbSession, current_user: CurrentUser):
    return create_organization(db, current_user, payload.name)


@router.get("/{organization_id}", response_model=OrganizationRead)
def read_org(organization_id: str, db: DbSession, current_user: CurrentUser):
    require_membership(db, organization_id, current_user)
    organization = get_organization(db, organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization
