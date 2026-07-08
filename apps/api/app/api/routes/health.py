from fastapi import APIRouter, Response, status
from redis import Redis
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine

router = APIRouter(tags=["health"])


def check_database() -> tuple[bool, str | None]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:
        return False, str(exc)


def check_redis() -> tuple[bool, str | None]:
    try:
        Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1).ping()
        return True, None
    except Exception as exc:
        return False, str(exc)


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/live")
def liveness_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def readiness_check(response: Response) -> dict:
    database_ok, database_error = check_database()
    redis_ok, redis_error = check_redis()
    ready = database_ok and redis_ok
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if ready else "unready",
        "dependencies": {
            "database": {"status": "ok" if database_ok else "error", "detail": database_error},
            "redis": {"status": "ok" if redis_ok else "error", "detail": redis_error},
        },
        "environment": settings.app_env,
        "release_version": settings.release_version,
    }
