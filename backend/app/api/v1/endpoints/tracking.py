from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.transactions import get_transaction_by_number, link_received_transactions_by_email
from app.schemas.tracking import RemittanceTrackingRead, StatusHistoryRead

router = APIRouter()


@router.get("/{remittance_number}", response_model=RemittanceTrackingRead)
def track_remittance(
    remittance_number: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    link_received_transactions_by_email(db, current_user.id, current_user.email)
    db.commit()
    transaction = get_transaction_by_number(db, remittance_number, current_user.id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "REMITTANCE_NOT_FOUND", "message": "Remesa no encontrada"},
        )
    return RemittanceTrackingRead(
        remittance_number=transaction.transaction_id,
        origin_country=transaction.origin_country,
        destination_country=transaction.destination_country,
        source_amount=transaction.source_amount,
        source_currency=transaction.source_currency,
        destination_amount=transaction.destination_amount,
        destination_currency=transaction.destination_currency,
        delivery_method=transaction.delivery_method,
        status=transaction.status,
        created_at=transaction.created_at,
        timeline=[StatusHistoryRead.model_validate(item) for item in transaction.status_history],
    )
