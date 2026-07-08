from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import settings
from app.core.encryption import encrypt_secret
from app.models.ai_triage_result import AITriageResult
from app.models.gmail_connection import GmailConnection
from app.models.gmail_draft import GmailDraft
from app.models.reply_approval import ReplyApproval
from app.models.ticket import Ticket


async def fake_refresh_gmail_access_token(refresh_token: str):
    return "access-token", None


async def fake_create_gmail_draft(access_token: str, raw_message: str, thread_id: str | None = None):
    return {"id": "draft-123", "message": {"threadId": thread_id}}


def create_ticket(client: TestClient, organization_id: str, subject: str) -> dict:
    response = client.post(
        f"/v1/orgs/{organization_id}/tickets",
        json={
            "customer_email": f"{subject.replace(' ', '').lower()}@example.com",
            "customer_name": "Casey Customer",
            "subject": subject,
            "message_text": "Please help with my order.",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_approved_reply(client: TestClient, organization_id: str, ticket_id: str, with_gmail: bool = True) -> str:
    with client.session_factory() as db:
        ticket = db.get(Ticket, ticket_id)
        gmail_connection_id = None
        if with_gmail:
            connection = GmailConnection(
                organization_id=organization_id,
                connected_by_user_id="user-owner",
                gmail_email="support@example.com",
                google_account_id="google-account-id",
                encrypted_refresh_token=encrypt_secret("refresh-token"),
                scopes="https://www.googleapis.com/auth/gmail.compose",
                status="active",
            )
            db.add(connection)
            db.flush()
            gmail_connection_id = connection.id
            ticket.gmail_connection_id = connection.id
            ticket.gmail_thread_id = "gmail-thread-id"
        triage = AITriageResult(
            organization_id=organization_id,
            ticket_id=ticket.id,
            model_name="gemini-test",
            raw_input={},
            raw_output={},
            validated_output={},
            category="product_question",
            priority="low",
            sentiment="neutral",
            summary="Customer has a question.",
            suggested_action="Answer the question.",
            draft_reply="Suggested reply.",
            requires_human_review=False,
        )
        db.add(triage)
        db.flush()
        approval = ReplyApproval(
            organization_id=organization_id,
            ticket_id=ticket.id,
            ai_triage_result_id=triage.id,
            gmail_connection_id=gmail_connection_id,
            suggested_reply="Suggested reply.",
            final_reply="Approved reply.",
            status="approved",
            reply_version=1,
            approved_reply_version=1,
            approved_by_user_id="user-owner",
        )
        db.add(approval)
        db.commit()
        return approval.id


def test_editing_approved_reply_invalidates_approval(client: TestClient, create_org) -> None:
    organization = create_org()
    ticket = create_ticket(client, organization["id"], "Order question")
    approval_id = create_approved_reply(client, organization["id"], ticket["id"])

    response = client.patch(
        f"/v1/orgs/{organization['id']}/tickets/{ticket['id']}/reply-approvals/{approval_id}",
        json={"final_reply": "Edited after approval."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending"
    assert body["reply_version"] == 2
    assert body["approved_reply_version"] is None
    assert body["approved_by_user_id"] is None


def test_closed_ticket_cannot_create_gmail_draft(client: TestClient, create_org, monkeypatch) -> None:
    monkeypatch.setattr(settings, "encryption_key", "test-encryption-key")
    organization = create_org()
    ticket = create_ticket(client, organization["id"], "Closed ticket")
    approval_id = create_approved_reply(client, organization["id"], ticket["id"], with_gmail=True)
    resolve_response = client.post(f"/v1/orgs/{organization['id']}/tickets/{ticket['id']}/resolve")
    assert resolve_response.status_code == 200
    monkeypatch.setattr("app.services.reply_approval_service.refresh_gmail_access_token", fake_refresh_gmail_access_token)
    monkeypatch.setattr("app.services.reply_approval_service.create_gmail_draft", fake_create_gmail_draft)

    response = client.post(f"/v1/orgs/{organization['id']}/reply-suggestions/{approval_id}/create-gmail-draft")

    assert response.status_code == 400
    assert response.json()["detail"] == "Closed tickets cannot create Gmail drafts"
    with client.session_factory() as db:
        assert db.scalar(select(GmailDraft)) is None


def test_ticket_list_supports_limit_and_offset(client: TestClient, create_org) -> None:
    organization = create_org()
    create_ticket(client, organization["id"], "First ticket")
    create_ticket(client, organization["id"], "Second ticket")
    create_ticket(client, organization["id"], "Third ticket")

    first_page = client.get(f"/v1/orgs/{organization['id']}/tickets?limit=1&offset=0")
    second_page = client.get(f"/v1/orgs/{organization['id']}/tickets?limit=1&offset=1")

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    assert len(first_page.json()) == 1
    assert len(second_page.json()) == 1
    assert first_page.json()[0]["id"] != second_page.json()[0]["id"]