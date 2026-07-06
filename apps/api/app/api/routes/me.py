from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.me import MeRead
from app.services.organization_service import list_user_organizations

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=MeRead)
def read_me(db: DbSession, current_user: CurrentUser) -> MeRead:
    return MeRead(
        id=current_user.id,
        email=current_user.email,
        organizations=list_user_organizations(db, current_user),
    )


@router.get("/organizations")
def read_my_organizations(db: DbSession, current_user: CurrentUser):
    return list_user_organizations(db, current_user)
