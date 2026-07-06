from fastapi.testclient import TestClient

from app.models.member import MemberRole, MemberStatus, OrganizationMember


def test_create_organization_makes_current_user_owner(client: TestClient, create_org) -> None:
    organization = create_org()

    response = client.get("/v1/me")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "user-owner"
    assert body["organizations"] == [
        {
            "id": organization["id"],
            "name": "Acme Support",
            "slug": "acme-support",
            "role": "owner",
        }
    ]


def test_user_cannot_access_organization_they_do_not_belong_to(
    client: TestClient,
    create_org,
) -> None:
    organization = create_org()
    client.current_user.update({"id": "different-user", "email": "different@example.com"})

    response = client.get(f"/v1/organizations/{organization['id']}")

    assert response.status_code == 403


def test_owner_can_invite_agent(client: TestClient, create_org) -> None:
    organization = create_org()

    response = client.post(
        f"/v1/orgs/{organization['id']}/members/invite",
        json={"email": "agent@example.com", "role": "agent"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "agent@example.com"
    assert body["role"] == "agent"
    assert body["status"] == "invited"


def test_agent_cannot_invite_members(client: TestClient, create_org) -> None:
    organization = create_org()
    with client.session_factory() as db:
        db.add(
            OrganizationMember(
                organization_id=organization["id"],
                user_id="agent-user",
                email="agent@example.com",
                role=MemberRole.AGENT.value,
                status=MemberStatus.ACTIVE.value,
            )
        )
        db.commit()

    client.current_user.update({"id": "agent-user", "email": "agent@example.com"})

    response = client.post(
        f"/v1/orgs/{organization['id']}/members/invite",
        json={"email": "new-agent@example.com", "role": "agent"},
    )

    assert response.status_code == 403


def test_admin_can_invite_agent_but_not_owner(client: TestClient, create_org) -> None:
    organization = create_org()
    with client.session_factory() as db:
        db.add(
            OrganizationMember(
                organization_id=organization["id"],
                user_id="admin-user",
                email="admin@example.com",
                role=MemberRole.ADMIN.value,
                status=MemberStatus.ACTIVE.value,
            )
        )
        db.commit()

    client.current_user.update({"id": "admin-user", "email": "admin@example.com"})

    agent_response = client.post(
        f"/v1/orgs/{organization['id']}/members/invite",
        json={"email": "new-agent@example.com", "role": "agent"},
    )
    owner_response = client.post(
        f"/v1/orgs/{organization['id']}/members/invite",
        json={"email": "new-owner@example.com", "role": "owner"},
    )

    assert agent_response.status_code == 201
    assert owner_response.status_code == 403
