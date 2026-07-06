from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.metrics import MetricsOverviewRead
from app.services.metrics_service import get_metrics_overview

router = APIRouter(tags=["metrics"])


@router.get("/orgs/{organization_id}/metrics/overview", response_model=MetricsOverviewRead)
def read_metrics_overview(organization_id: str, db: DbSession, current_user: CurrentUser):
    return get_metrics_overview(db, organization_id, current_user)