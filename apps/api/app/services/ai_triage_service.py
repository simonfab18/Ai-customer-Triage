from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser
from app.integrations.gemini.client import classify_ticket_with_gemini
from app.integrations.gemini.prompts import build_triage_prompt
from app.models.ai_triage_result import AITriageResult
from app.models.reply_approval import ReplyApproval
from app.models.ticket import TicketCategory, TicketPriority
from app.schemas.ai import TriageOutput
from app.services.reply_suggestion_service import create_ai_reply_suggestion_from_triage
from app.services.ticket_service import get_ticket_or_404, write_ticket_event

REVIEW_REQUIRED_CATEGORIES = {
    TicketCategory.REFUND.value,
    TicketCategory.RETURN.value,
    TicketCategory.DAMAGED_ITEM.value,
    TicketCategory.BILLING.value,
    TicketCategory.ACCOUNT_ACCESS.value,
    TicketCategory.COMPLAINT.value,
}

REVIEW_KEYWORDS = {
    "refund",
    "replacement",
    "cancel",
    "cancellation",
    "credit",
    "compensation",
    "chargeback",
    "fraud",
    "legal",
    "privacy",
    "unsafe",
    "injury",
}


def enforce_human_review(output: TriageOutput, subject: str, message: str) -> bool:
    if output.requires_human_review:
        return True
    if output.priority in {TicketPriority.CRITICAL, TicketPriority.HIGH}:
        return True
    if output.category.value in REVIEW_REQUIRED_CATEGORIES:
        return True

    text = f"{subject} {message}".lower()
    return any(keyword in text for keyword in REVIEW_KEYWORDS)


async def run_ticket_triage(
    db: Session,
    organization_id: str,
    ticket_id: str,
    actor: AuthenticatedUser,
) -> AITriageResult:
    ticket = get_ticket_or_404(db, organization_id, ticket_id, actor)
    prompt = build_triage_prompt(
        customer_name=ticket.customer.name,
        customer_email=ticket.customer.email,
        subject=ticket.subject,
        message=ticket.message_text,
    )
    output, raw_output = await classify_ticket_with_gemini(prompt)
    requires_human_review = enforce_human_review(output, ticket.subject, ticket.message_text)

    ticket.category = output.category.value
    ticket.priority = output.priority.value
    ticket.sentiment = output.sentiment.value

    validated_output = output.model_dump(mode="json")
    validated_output["requires_human_review"] = requires_human_review

    result = AITriageResult(
        organization_id=organization_id,
        ticket_id=ticket.id,
        model_name=raw_output.get("model") or "gemini",
        raw_input={"prompt": prompt},
        raw_output=raw_output,
        validated_output=validated_output,
        category=output.category.value,
        priority=output.priority.value,
        sentiment=output.sentiment.value,
        summary=output.summary,
        suggested_action=output.suggested_action,
        draft_reply=output.draft_reply,
        confidence_score=output.confidence_score,
        reasoning=output.reasoning,
        requires_human_review=requires_human_review,
        validation_status="valid",
    )
    db.add(result)
    db.flush()
    create_ai_reply_suggestion_from_triage(db, ticket.id, result, ticket.gmail_connection_id)
    db.add(
        ReplyApproval(
            organization_id=organization_id,
            ticket_id=ticket.id,
            ai_triage_result_id=result.id,
            gmail_connection_id=ticket.gmail_connection_id,
            suggested_reply=result.draft_reply,
            final_reply=result.draft_reply,
        )
    )
    db.flush()

    write_ticket_event(
        db,
        ticket,
        actor,
        "ticket.ai_triaged",
        {
            "ai_triage_result_id": result.id,
            "model_provider": result.model_provider,
            "model_name": result.model_name,
            "priority": result.priority,
            "category": result.category,
            "requires_human_review": result.requires_human_review,
            "confidence_score": result.confidence_score,
        },
    )
    db.commit()
    db.refresh(result)
    return result


def list_ticket_triage_results(
    db: Session,
    organization_id: str,
    ticket_id: str,
    actor: AuthenticatedUser,
) -> list[AITriageResult]:
    get_ticket_or_404(db, organization_id, ticket_id, actor)
    return list(
        db.scalars(
            select(AITriageResult)
            .where(
                AITriageResult.organization_id == organization_id,
                AITriageResult.ticket_id == ticket_id,
            )
            .order_by(AITriageResult.created_at.desc())
        )
    )