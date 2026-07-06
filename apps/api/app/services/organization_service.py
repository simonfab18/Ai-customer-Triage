from re import sub
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser
from app.models.member import MemberRole, MemberStatus, OrganizationMember
from app.models.organization import Organization
from app.schemas.organization import UserOrganizationRead


def make_slug(name: str) -> str:
    base = sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return base or "organization"


def unique_slug(db: Session, name: str) -> str:
    base = make_slug(name)
    slug = base
    suffix = 2
    while db.scalar(select(Organization).where(Organization.slug == slug)) is not None:
        slug = f"{base}-{suffix}"
        suffix += 1
    return slug


def create_organization(db: Session, user: AuthenticatedUser, name: str) -> Organization:
    organization = Organization(name=name.strip(), slug=unique_slug(db, name))
    db.add(organization)
    db.flush()

    member = OrganizationMember(
        organization_id=organization.id,
        user_id=user.id,
        email=user.email or "unknown@example.local",
        role=MemberRole.OWNER.value,
        status=MemberStatus.ACTIVE.value,
    )
    db.add(member)
    db.commit()
    db.refresh(organization)
    return organization


def list_user_organizations(db: Session, user: AuthenticatedUser) -> list[UserOrganizationRead]:
    rows = db.execute(
        select(Organization, OrganizationMember)
        .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
        .where(
            OrganizationMember.user_id == user.id,
            OrganizationMember.status == MemberStatus.ACTIVE.value,
        )
        .order_by(Organization.created_at.desc())
    ).all()
    return [
        UserOrganizationRead(
            id=organization.id,
            name=organization.name,
            slug=organization.slug,
            role=member.role,
        )
        for organization, member in rows
    ]


def get_organization(db: Session, organization_id: str) -> Organization | None:
    return db.get(Organization, organization_id)


def placeholder_user_id_for_email(email: str) -> str:
    normalized = email.strip().lower()
    return f"invited:{normalized}:{uuid4()}"

