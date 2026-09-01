from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.forecasting import ForecastCorridorItem, ForecastModelInfo, ForecastResponse, ForecastSummary
from app.services.forecasting import generate_forecast, get_corridor_forecasts, get_forecast_model_info, get_forecast_summary

router = APIRouter()


def require_forecasting_access(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name not in {"ADMIN", "RISK_ANALYST"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORECASTING_FORBIDDEN", "message": "Analitica predictiva disponible solo para perfiles autorizados"},
        )
    return current_user


@router.get("/model-info", response_model=ForecastModelInfo)
def read_model_info(_: User = Depends(require_forecasting_access)):
    return get_forecast_model_info()


@router.get("/summary", response_model=ForecastSummary)
def read_summary(_: User = Depends(require_forecasting_access)):
    return get_forecast_summary()


@router.get("/volume", response_model=ForecastResponse)
def read_volume_forecast(
    horizon: int = Query(default=8),
    granularity: str = Query(default="weekly"),
    _: User = Depends(require_forecasting_access),
    db: Session = Depends(get_db),
):
    return generate_forecast("transaction_count", horizon, granularity, db=db, persist=True)


@router.get("/amount", response_model=ForecastResponse)
def read_amount_forecast(
    horizon: int = Query(default=8),
    granularity: str = Query(default="weekly"),
    _: User = Depends(require_forecasting_access),
    db: Session = Depends(get_db),
):
    return generate_forecast("transaction_amount_usd", horizon, granularity, db=db, persist=True)


@router.get("/corridors", response_model=list[ForecastCorridorItem])
def read_corridor_forecasts(horizon: int = Query(default=4), _: User = Depends(require_forecasting_access)):
    return get_corridor_forecasts(horizon)
