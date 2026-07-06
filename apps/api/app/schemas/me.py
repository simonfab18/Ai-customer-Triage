from pydantic import BaseModel

from app.schemas.organization import UserOrganizationRead


class MeRead(BaseModel):
    id: str
    email: str | None = None
    organizations: list[UserOrganizationRead]
