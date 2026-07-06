from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser
from app.models.member import MemberRole, MemberStatus, OrganizationMember
from app.schemas.member import MemberInvite, MemberUpdate
from app.services.organization_service import placeholder_user_id_for_email
from app.services.rbac_service import can_manage_role, require_role


def list_members(db: Session, organization_id: str) -> list[OrganizationMember]:
    return list(
        db.scalars(
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == organization_id)
            .order_by(OrganizationMember.created_at.asc())
        )
    )


def invite_member(
    db: Session,
    organization_id: str,
    actor: AuthenticatedUser,
    payload: MemberInvite,
) -> OrganizationMember:
    actor_membership = require_role(
        db,
        organization_id,
        actor,
        {MemberRole.OWNER, MemberRole.ADMIN},
    )
    if not can_manage_role(actor_membership.role, payload.role.value):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot assign that role")

    email = payload.email.strip().lower()
    existing = db.scalar(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.email == email,
            OrganizationMember.status != MemberStatus.DISABLED.value,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member already exists")

    member = OrganizationMember(
        organization_id=organization_id,
        user_id=placeholder_user_id_for_email(email),
        email=email,
        role=payload.role.value,
        status=MemberStatus.INVITED.value,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_member(
    db: Session,
    organization_id: str,
    member_id: str,
    actor: AuthenticatedUser,
    payload: MemberUpdate,
) -> OrganizationMember:
    actor_membership = require_role(
        db,
        organization_id,
        actor,
        {MemberRole.OWNER, MemberRole.ADMIN},
    )
    member = db.get(OrganizationMember, member_id)
    if member is None or member.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == MemberRole.OWNER.value and actor_membership.role != MemberRole.OWNER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify owner")

    next_role = payload.role.value if payload.role else member.role
    if not can_manage_role(actor_membership.role, next_role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot assign that role")

    if payload.role is not None:
        member.role = payload.role.value
    if payload.status is not None:
        member.status = payload.status.value

    db.commit()
    db.refresh(member)
    return member


def remove_member(db: Session, organization_id: str, member_id: str, actor: AuthenticatedUser) -> None:
    actor_membership = require_role(
        db,
        organization_id,
        actor,
        {MemberRole.OWNER, MemberRole.ADMIN},
    )
    member = db.get(OrganizationMember, member_id)
    if member is None or member.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == MemberRole.OWNER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot remove owner")
    if not can_manage_role(actor_membership.role, member.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot remove that member")

    member.status = MemberStatus.DISABLED.value
    db.commit()
