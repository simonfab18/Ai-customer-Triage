from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser
from app.models.ai_triage_result import AITriageResult
from app.models.gmail_sync_event import GmailSyncEvent
from app.models.job_run import JobRun, JobRunStatus
from app.models.ticket import Ticket, TicketTriageStatus
from app.services.ai_triage_service import PROMPT_VERSION, SCHEMA_VERSION
from app.services.email_import_service import create_gmail_import_job
from app.services.gmail_history_sync_service import create_history_sync_event, list_stale_connections
from app.services.workspace_settings_service import get_or_create_workspace_settings
from app.worker.tasks import history_sync_gmail_connection_task, sync_gmail_connection_task


def enqueue_gmail_import(
    db: Session,
    organization_id: str,
    connection_id: str,
    actor: AuthenticatedUser,
    max_results: int = 20,
) -> JobRun:
    job = create_gmail_import_job(db, organization_id, connection_id, actor, max_results=max_results)
    try:
        sync_gmail_connection_task.delay(
            job.id,
            organization_id,
            connection_id,
            actor.id,
            actor.email,
            max_results,
        )
        db.refresh(job)
    except Exception as exc:
        job.status = "failed"
        job.error_message = f"Could not enqueue Gmail import job: {exc}"
        db.commit()
        db.refresh(job)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not enqueue Gmail import job. Is Redis/Celery running?",
        ) from exc
    return job


def enqueue_ticket_triage(
    db: Session,
    organization_id: str,
    ticket_id: str,
    actor: AuthenticatedUser,
    *,
    force: bool = False,
    respect_workspace_setting: bool = True,
    raise_on_enqueue_error: bool = True,
) -> JobRun | None:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None or ticket.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    settings = get_or_create_workspace_settings(db, organization_id)
    if respect_workspace_setting and not settings.auto_triage_enabled:
        ticket.triage_status = TicketTriageStatus.NOT_QUEUED.value
        db.commit()
        return None

    if not force and ticket.active_triage_job_id:
        active_job = db.get(JobRun, ticket.active_triage_job_id)
        if active_job is not None and active_job.status in {JobRunStatus.QUEUED.value, JobRunStatus.RUNNING.value}:
            return active_job

    if not force and ticket.triage_status == TicketTriageStatus.TRIAGED.value:
        has_result = db.scalar(
            select(AITriageResult.id).where(
                AITriageResult.organization_id == organization_id,
                AITriageResult.ticket_id == ticket_id,
            )
        )
        if has_result:
            return None

    job = JobRun(
        organization_id=organization_id,
        job_type="ai_triage",
        status=JobRunStatus.QUEUED.value,
        job_metadata={
            "ticket_id": ticket_id,
            "requested_by_user_id": actor.id,
            "prompt_version": PROMPT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "manual_retry": force,
        },
    )
    db.add(job)
    db.flush()
    ticket.triage_status = TicketTriageStatus.QUEUED.value
    ticket.active_triage_job_id = job.id
    ticket.triage_error_message = None
    db.commit()
    db.refresh(job)

    try:
        from app.worker.tasks import triage_ticket_task

        triage_ticket_task.delay(job.id)
    except Exception as exc:
        job.status = JobRunStatus.FAILED.value
        job.error_message = f"Could not enqueue AI triage job: {exc}"
        job.finished_at = None
        ticket.triage_status = TicketTriageStatus.FAILED.value
        ticket.active_triage_job_id = None
        ticket.triage_error_message = job.error_message
        db.commit()
        db.refresh(job)
        if raise_on_enqueue_error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not enqueue AI triage job. Is Redis/Celery running?",
            ) from exc
    return job


def enqueue_gmail_history_sync(
    db: Session,
    organization_id: str,
    connection_id: str,
    *,
    trigger_type: str = "manual_history_sync",
    pubsub_message_id: str | None = None,
    notification_history_id: str | None = None,
    metadata: dict | None = None,
) -> GmailSyncEvent:
    from app.models.gmail_connection import GmailConnection

    connection = db.get(GmailConnection, connection_id)
    if connection is None or connection.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gmail connection not found")
    if connection.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gmail connection is not active")

    event = create_history_sync_event(
        db,
        connection,
        trigger_type=trigger_type,
        pubsub_message_id=pubsub_message_id,
        notification_history_id=notification_history_id,
        metadata=metadata,
    )
    db.commit()
    db.refresh(event)
    try:
        history_sync_gmail_connection_task.delay(
            organization_id,
            connection_id,
            event.id,
            notification_history_id,
            trigger_type,
        )
    except Exception as exc:
        event.status = "failed"
        event.error_code = "enqueue_failed"
        event.error_message = f"Could not enqueue Gmail history sync job: {exc}"
        db.commit()
        db.refresh(event)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not enqueue Gmail history sync job. Is Redis/Celery running?",
        ) from exc
    return event


def enqueue_fallback_syncs(db: Session) -> list[GmailSyncEvent]:
    events: list[GmailSyncEvent] = []
    for connection in list_stale_connections(db):
        event = enqueue_gmail_history_sync(
            db,
            connection.organization_id,
            connection.id,
            trigger_type="fallback_sync",
            metadata={"reason": "stale_connection_scan"},
        )
        events.append(event)
    return events