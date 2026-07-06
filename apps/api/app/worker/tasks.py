import asyncio

from app.api.deps import AuthenticatedUser
from app.db.session import SessionLocal
from app.services.email_import_service import run_gmail_import_job
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
