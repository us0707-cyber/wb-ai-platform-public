from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, require_roles
from src.database.session import get_db
from src.models import User
from src.schemas.analytics import ABCXYZItem, AnalyticsOverview, AnalyticsPoint, ForecastItem
from src.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def overview(
    days: int = Query(default=30, ge=7, le=365),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).overview(user.id, days)


@router.get("/trends", response_model=list[AnalyticsPoint])
def trends(
    days: int = Query(default=30, ge=7, le=365),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).trends(user.id, days)


@router.get("/abc-xyz", response_model=list[ABCXYZItem])
def abc_xyz(
    days: int = Query(default=30, ge=7, le=365),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).abc_xyz(user.id, days)


@router.get("/forecast", response_model=list[ForecastItem])
def forecast(
    history_days: int = Query(default=30, ge=7, le=365),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).forecast(user.id, history_days)


@router.post("/demo/generate")
def generate_demo(
    days: int = Query(default=60, ge=30, le=365),
    user: User = Depends(require_roles("admin", "manager")),
    db: Session = Depends(get_db),
):
    created = AnalyticsService(db).seed_demo(user.id, days)
    return {"ok": True, "created": created, "days": days}
