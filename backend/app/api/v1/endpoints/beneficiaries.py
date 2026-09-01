from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.beneficiaries import create_beneficiary, get_beneficiary, list_beneficiaries, update_beneficiary
from app.schemas.beneficiary import BeneficiaryCreate, BeneficiaryRead, BeneficiaryUpdate
from app.services.audit import log_audit_event

router = APIRouter()


@router.get("", response_model=list[BeneficiaryRead])
def read_beneficiaries(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_beneficiaries(db, current_user.id)


@router.post("", response_model=BeneficiaryRead, status_code=status.HTTP_201_CREATED)
def create_new_beneficiary(
    payload: BeneficiaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        beneficiary = create_beneficiary(db, current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": str(exc), "message": "Datos de beneficiario no validos"},
        ) from None
    log_audit_event(
        db,
        user_id=current_user.id,
        action="BENEFICIARY_CREATED",
        entity="beneficiary",
        entity_id=str(beneficiary.id),
    )
    db.commit()
    db.refresh(beneficiary)
    return beneficiary


@router.get("/{beneficiary_id}", response_model=BeneficiaryRead)
def read_beneficiary(
    beneficiary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    beneficiary = get_beneficiary(db, beneficiary_id, current_user.id)
    if beneficiary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "BENEFICIARY_NOT_FOUND", "message": "Beneficiario no encontrado"},
        )
    return beneficiary


@router.patch("/{beneficiary_id}", response_model=BeneficiaryRead)
def patch_beneficiary(
    beneficiary_id: int,
    payload: BeneficiaryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    beneficiary = get_beneficiary(db, beneficiary_id, current_user.id)
    if beneficiary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "BENEFICIARY_NOT_FOUND", "message": "Beneficiario no encontrado"},
        )

    try:
        update_beneficiary(db, beneficiary, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": str(exc), "message": "Datos de beneficiario no validos"},
        ) from None
    log_audit_event(
        db,
        user_id=current_user.id,
        action="BENEFICIARY_UPDATED",
        entity="beneficiary",
        entity_id=str(beneficiary.id),
        metadata={"fields": sorted(payload.model_dump(exclude_unset=True).keys())},
    )
    db.commit()
    db.refresh(beneficiary)
    return beneficiary
