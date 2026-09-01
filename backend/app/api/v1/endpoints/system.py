from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.assistant.service import assistant_info
from app.blockchain.config import BLOCKCHAIN_ENGINE_VERSION, DEFAULT_DIFFICULTY
from app.core.config import settings
from app.core.observability import metrics_registry
from app.core.version import API_VERSION, APP_VERSION
from app.db.session import get_db
from app.models.user import User
from app.services.forecasting import get_forecast_model_info
from app.services.risk_engine import risk_engine_info

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "ADMIN_REQUIRED", "message": "Operacion disponible solo para administrador"})
    return current_user


@router.get("/info")
def system_info(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    database_type = settings.database_url.split(":", 1)[0]
    db.execute(text("SELECT 1"))
    risk_info = risk_engine_info()
    forecast_info = get_forecast_model_info()
    assistant = assistant_info()
    return {
        "app_name": settings.app_name,
        "app_version": APP_VERSION,
        "api_version": API_VERSION,
        "environment": settings.environment,
        "database": {"type": database_type, "status": "ok"},
        "risk_engine_version": risk_info.get("risk_engine_version"),
        "ml_model_version": risk_info.get("ml_model_version"),
        "ml_threshold": risk_info.get("ml_threshold"),
        "forecast_version": forecast_info.get("version"),
        "blockchain_version": BLOCKCHAIN_ENGINE_VERSION,
        "blockchain_difficulty": DEFAULT_DIFFICULTY,
        "assistant_provider_type": assistant["provider"],
        "assistant_provider_status": assistant["provider_status"],
    }


@router.get("/metrics")
def system_metrics(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {
        "app_version": APP_VERSION,
        "environment": settings.environment,
        "database": "ok",
        "requests": metrics_registry.snapshot(),
        "assistant": assistant_info(),
    }
