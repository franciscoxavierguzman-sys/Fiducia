from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.bi.filters import BIFilters
from app.db.session import get_db
from app.models.user import User
from app.services.business_intelligence import (
    export_corridors_csv,
    export_kpis_csv,
    get_bi_corridors,
    get_bi_customers,
    get_bi_forecast,
    get_bi_kpis,
    get_bi_operations,
    get_bi_overview,
    get_bi_risk,
    get_bi_trends,
    get_executive_summary,
)

router = APIRouter()


def require_bi_access(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name not in {"ADMIN", "RISK_ANALYST"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "BI_FORBIDDEN", "message": "Inteligencia de negocio disponible solo para perfiles autorizados"},
        )
    return current_user


def bi_filters(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    origin_country: str | None = None,
    destination_country: str | None = None,
    currency: str | None = Query(default=None, min_length=3, max_length=3),
    status: str | None = None,
) -> BIFilters:
    return BIFilters(date_from=date_from, date_to=date_to, origin_country=origin_country, destination_country=destination_country, currency=currency, status=status)


@router.get("/kpis")
def read_kpis(_: User = Depends(require_bi_access)) -> list[dict]:
    return get_bi_kpis()


@router.get("/overview")
def read_overview(filters: BIFilters = Depends(bi_filters), _: User = Depends(require_bi_access), db: Session = Depends(get_db)) -> dict:
    return get_bi_overview(db, filters)


@router.get("/trends")
def read_trends(
    granularity: str = Query(default="week", pattern="^(day|week|month)$"),
    filters: BIFilters = Depends(bi_filters),
    _: User = Depends(require_bi_access),
    db: Session = Depends(get_db),
) -> list[dict]:
    return get_bi_trends(db, filters, granularity)


@router.get("/corridors")
def read_corridors(filters: BIFilters = Depends(bi_filters), _: User = Depends(require_bi_access), db: Session = Depends(get_db)) -> list[dict]:
    return get_bi_corridors(db, filters)


@router.get("/customers")
def read_customers(filters: BIFilters = Depends(bi_filters), _: User = Depends(require_bi_access), db: Session = Depends(get_db)) -> dict:
    return get_bi_customers(db, filters)


@router.get("/operations")
def read_operations(filters: BIFilters = Depends(bi_filters), _: User = Depends(require_bi_access), db: Session = Depends(get_db)) -> dict:
    return get_bi_operations(db, filters)


@router.get("/risk")
def read_risk(filters: BIFilters = Depends(bi_filters), _: User = Depends(require_bi_access), db: Session = Depends(get_db)) -> dict:
    return get_bi_risk(db, filters)


@router.get("/forecast")
def read_forecast(_: User = Depends(require_bi_access)) -> dict:
    return get_bi_forecast()


@router.get("/executive-summary")
def read_executive_summary(filters: BIFilters = Depends(bi_filters), _: User = Depends(require_bi_access), db: Session = Depends(get_db)) -> dict:
    return get_executive_summary(db, filters)


@router.get("/exports/kpis.csv")
def export_kpis(filters: BIFilters = Depends(bi_filters), _: User = Depends(require_bi_access), db: Session = Depends(get_db)) -> Response:
    return Response(content=export_kpis_csv(db, filters), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=kpis.csv"})


@router.get("/exports/corridors.csv")
def export_corridors(filters: BIFilters = Depends(bi_filters), _: User = Depends(require_bi_access), db: Session = Depends(get_db)) -> Response:
    return Response(content=export_corridors_csv(db, filters), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=corridors.csv"})
