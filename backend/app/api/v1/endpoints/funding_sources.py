from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.funding_sources import (
    create_funding_source,
    get_funding_source,
    list_funding_sources,
    set_default_funding_source,
    update_funding_source,
)
from app.schemas.funding_source import FundingSourceCreate, FundingSourceRead, FundingSourceUpdate
from app.services.audit import log_audit_event

router = APIRouter()


@router.get("", response_model=list[FundingSourceRead])
def read_funding_sources(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_funding_sources(db, current_user.id)


@router.post("", response_model=FundingSourceRead, status_code=status.HTTP_201_CREATED)
def create_new_funding_source(
    payload: FundingSourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    source = create_funding_source(db, current_user.id, payload)
    log_audit_event(
        db,
        user_id=current_user.id,
        action="FUNDING_SOURCE_ADDED",
        entity="funding_source",
        entity_id=str(source.id),
        metadata={"type": source.type, "currency": source.currency},
    )
    db.commit()
    db.refresh(source)
    return source


@router.patch("/{funding_source_id}", response_model=FundingSourceRead)
def patch_funding_source(
    funding_source_id: int,
    payload: FundingSourceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    source = get_funding_source(db, funding_source_id, current_user.id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FUNDING_SOURCE_NOT_FOUND", "message": "Metodo de pago no encontrado"},
        )
    update_funding_source(db, source, payload)
    db.commit()
    db.refresh(source)
    return source


@router.post("/{funding_source_id}/default", response_model=FundingSourceRead)
def make_default_funding_source(
    funding_source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    source = get_funding_source(db, funding_source_id, current_user.id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FUNDING_SOURCE_NOT_FOUND", "message": "Metodo de pago no encontrado"},
        )
    set_default_funding_source(db, source)
    db.commit()
    db.refresh(source)
    return source
