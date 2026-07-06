from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser
from app.models.job_run import JobRun
from app.services.email_import_service import create_gmail_import_job
from app.worker.tasks import sync_gmail_connection_task


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
