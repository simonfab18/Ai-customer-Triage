from fastapi import APIRouter

from app.api.routes.health import check_database, check_redis
from app.core.config import settings
from app.schemas.operations import ServiceStatusRead, StatusDependencyRead

router = APIRouter(tags=["status"])


@router.get("/status", response_model=ServiceStatusRead)
def status() -> ServiceStatusRead:
    database_ok, database_error = check_database()
    redis_ok, redis_error = check_redis()
    service_ok = database_ok and redis_ok
    return ServiceStatusRead(
        service=settings.app_name,
        environment=settings.app_env,
        release_version=settings.release_version,
        status="ok" if service_ok else "degraded",
        dependencies={
            "database": StatusDependencyRead(status="ok" if database_ok else "error", detail=database_error),
            "redis": StatusDependencyRead(status="ok" if redis_ok else "error", detail=redis_error),
        },
    )
