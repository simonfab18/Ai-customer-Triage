from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser
from app.models.member import MemberRole, MemberStatus, OrganizationMember
from app.models.organization import Organization

ROLE_ORDER = {
    MemberRole.AGENT.value: 1,
    MemberRole.ADMIN.value: 2,
    MemberRole.OWNER.value: 3,
}


def get_membership(db: Session, organization_id: str, user_id: str) -> OrganizationMember | None:
    return db.scalar(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
            OrganizationMember.status == MemberStatus.ACTIVE.value,
        )
    )


def require_membership(db: Session, organization_id: str, user: AuthenticatedUser) -> OrganizationMember:
    organization = db.get(Organization, organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    membership = get_membership(db, organization_id, user.id)
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")
    return membership


def require_role(
    db: Session,
    organization_id: str,
    user: AuthenticatedUser,
    allowed_roles: set[MemberRole],
) -> OrganizationMember:
    membership = require_membership(db, organization_id, user)
    allowed = {role.value for role in allowed_roles}
    if membership.role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return membership


def can_manage_role(actor_role: str, target_role: str) -> bool:
    if actor_role == MemberRole.OWNER.value:
        return True
    if actor_role == MemberRole.ADMIN.value:
        return target_role == MemberRole.AGENT.value
    return False
