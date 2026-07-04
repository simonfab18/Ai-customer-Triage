from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["status"])


@router.get("/status")
def status() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "environment": settings.app_env,
        "status": "ok",
    }

