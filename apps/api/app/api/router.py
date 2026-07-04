from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.status import router as status_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(status_router, prefix="/v1")

