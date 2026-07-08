import asyncio

from app.api.deps import AuthenticatedUser
from app.db.session import SessionLocal
from app.services.email_import_service import run_gmail_import_job
from app.services.gmail_history_sync_service import run_gmail_history_sync
from app.services.gmail_watch_service import renew_gmail_watch
from app.services.ai_triage_service import run_ticket_triage_job
from app.worker.celery_app import celery_app


@celery_app.task(name="gmail.sync_connection")
def sync_gmail_connection_task(
    job_id: str,
    organization_id: str,
    connection_id: str,
    actor_id: str,
    actor_email: str | None,
    max_results: int,
) -> str:
    actor = AuthenticatedUser(id=actor_id, email=actor_email)
    db = SessionLocal()
    try:
        job = asyncio.run(
            run_gmail_import_job(
                db,
                job_id,
                organization_id,
                connection_id,
                actor,
                max_results=max_results,
            )
        )
        return job.id
    finally:
        db.close()


@celery_app.task(name="gmail.history_sync_connection")
def history_sync_gmail_connection_task(
    organization_id: str,
    connection_id: str,
    event_id: str,
    notification_history_id: str | None = None,
    trigger_type: str = "history_sync",
) -> str:
    db = SessionLocal()
    try:
        event = asyncio.run(
            run_gmail_history_sync(
                db,
                organization_id,
                connection_id,
                event_id=event_id,
                notification_history_id=notification_history_id,
                trigger_type=trigger_type,
            )
        )
        return event.id
    finally:
        db.close()


@celery_app.task(name="gmail.renew_watch")
def renew_gmail_watch_task(organization_id: str, connection_id: str) -> str:
    db = SessionLocal()
    try:
        connection, event = asyncio.run(
            renew_gmail_watch(
                db,
                organization_id,
                connection_id,
                actor=None,
            )
        )
        return event.id or connection.id
    finally:
        db.close()


@celery_app.task(name="gmail.enqueue_fallback_syncs")
def enqueue_fallback_syncs_task() -> list[str]:
    db = SessionLocal()
    try:
        from app.services.job_queue_service import enqueue_fallback_syncs

        events = enqueue_fallback_syncs(db)
        return [event.id for event in events]
    finally:
        db.close()

@celery_app.task(name="ai.triage_ticket")
def triage_ticket_task(job_id: str) -> str:
    db = SessionLocal()
    try:
        result = asyncio.run(run_ticket_triage_job(db, job_id))
        return result.id
    finally:
        db.close()