from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser
from app.models.gmail_sync_event import GmailSyncEvent
from app.models.job_run import JobRun
from app.services.email_import_service import create_gmail_import_job
from app.services.gmail_history_sync_service import create_history_sync_event, list_stale_connections
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
