from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsDistributionItem, AnalyticsSummary, AnalyticsTimeSeriesPoint
from app.services.analytics import (
    get_analytics_summary,
    get_currency_distribution,
    get_method_distribution,
    get_remittances_over_time,
    get_status_distribution,
    get_top_corridors,
)

router = APIRouter()


def require_analytics_access(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name not in {"ADMIN", "RISK_ANALYST"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ANALYTICS_FORBIDDEN", "message": "Analitica disponible solo para perfiles autorizados"},
        )
    return current_user


@router.get("/summary", response_model=AnalyticsSummary)
def read_analytics_summary(
    _: User = Depends(require_analytics_access),
    db: Session = Depends(get_db),
) -> AnalyticsSummary:
    return get_analytics_summary(db)


@router.get("/remittances-over-time", response_model=list[AnalyticsTimeSeriesPoint])
def read_remittances_over_time(
    _: User = Depends(require_analytics_access),
    db: Session = Depends(get_db),
) -> list[AnalyticsTimeSeriesPoint]:
    return get_remittances_over_time(db)


@router.get("/top-corridors", response_model=list[AnalyticsDistributionItem])
def read_top_corridors(
    _: User = Depends(require_analytics_access),
    db: Session = Depends(get_db),
) -> list[AnalyticsDistributionItem]:
    return get_top_corridors(db)


@router.get("/status-distribution", response_model=list[AnalyticsDistributionItem])
def read_status_distribution(
    _: User = Depends(require_analytics_access),
    db: Session = Depends(get_db),
) -> list[AnalyticsDistributionItem]:
    return get_status_distribution(db)


@router.get("/currency-distribution", response_model=list[AnalyticsDistributionItem])
def read_currency_distribution(
    _: User = Depends(require_analytics_access),
    db: Session = Depends(get_db),
) -> list[AnalyticsDistributionItem]:
    return get_currency_distribution(db)


@router.get("/method-distribution", response_model=dict[str, list[AnalyticsDistributionItem]])
def read_method_distribution(
    _: User = Depends(require_analytics_access),
    db: Session = Depends(get_db),
) -> dict[str, list[AnalyticsDistributionItem]]:
    return get_method_distribution(db)
