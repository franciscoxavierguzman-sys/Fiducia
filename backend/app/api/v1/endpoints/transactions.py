from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.transactions import (
    get_received_transaction,
    get_transaction,
    link_received_transactions_by_email,
    list_received_transactions,
    list_sent_transactions,
    list_transactions,
)
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.audit import log_audit_event
from app.services.blockchain import record_remittance_event
from app.services.remittances import simulate_remittance
from app.services.risk_engine import evaluate_remittance
from app.services.status_history import record_status_change

router = APIRouter()


@router.get("", response_model=list[TransactionRead])
def read_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_transactions(db, current_user.id)


@router.get("/sent", response_model=list[TransactionRead])
def read_sent_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_sent_transactions(db, current_user.id)


@router.get("/received", response_model=list[TransactionRead])
def read_received_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    link_received_transactions_by_email(db, current_user.id, current_user.email)
    db.commit()
    return list_received_transactions(db, current_user.id)


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    simulation = simulate_remittance(db, payload, current_user.id)
    transaction = Transaction(
        remittance_uuid=str(uuid4()),
        sender_id=current_user.id,
        beneficiary_id=payload.beneficiary_id,
        beneficiary_user_id=simulation.beneficiary_user_id,
        funding_source_id=payload.funding_source_id,
        origin_country=simulation.origin_country,
        destination_country=simulation.destination_country,
        source_amount=simulation.source_amount,
        source_currency=simulation.source_currency,
        destination_currency=simulation.destination_currency,
        amount=simulation.amount,
        currency=simulation.currency,
        exchange_rate=simulation.exchange_rate,
        commission_rate=simulation.commission_rate,
        commission_amount=simulation.commission_amount,
        total_amount=simulation.total_amount,
        debit_amount=simulation.total_debit_amount,
        debit_currency=simulation.total_debit_currency,
        destination_amount=simulation.destination_amount,
        payment_method=simulation.payment_method,
        delivery_method=simulation.delivery_method,
        status="AVAILABLE",
        model_version=None,
    )
    db.add(transaction)
    db.flush()
    transaction.transaction_id = f"FID-{datetime.now(UTC).year}-{transaction.id:06d}"
    record_status_change(
        db,
        transaction,
        previous_status=None,
        new_status=transaction.status,
        changed_by=current_user.id,
        reason="REMITTANCE_CREATED",
    )
    log_audit_event(
        db,
        user_id=current_user.id,
        action="REMITTANCE_CREATED",
        entity="transaction",
        entity_id=transaction.transaction_id,
        metadata={"status": transaction.status, "beneficiary_user_id": transaction.beneficiary_user_id},
    )
    record_remittance_event(db, transaction, "REMITTANCE_CREATED", current_user.id)
    record_remittance_event(db, transaction, "REMITTANCE_AVAILABLE", current_user.id)
    evaluate_remittance(db, transaction, actor_user_id=current_user.id)
    db.commit()
    db.refresh(transaction)
    return get_transaction(db, transaction.id, current_user.id)


@router.post("/{transaction_id}/receive", response_model=TransactionRead)
def receive_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    link_received_transactions_by_email(db, current_user.id, current_user.email)
    transaction = get_received_transaction(db, transaction_id, current_user.id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TRANSACTION_NOT_FOUND", "message": "Remesa recibida no encontrada"},
        )
    if transaction.status != "AVAILABLE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_TRANSACTION_STATUS", "message": "La remesa no esta disponible para recibir"},
        )
    previous_status = transaction.status
    transaction.status = "COMPLETED"
    transaction.updated_at = datetime.now(UTC)
    record_status_change(
        db,
        transaction,
        previous_status=previous_status,
        new_status=transaction.status,
        changed_by=current_user.id,
        reason="REMITTANCE_RECEIVED",
    )
    log_audit_event(
        db,
        user_id=current_user.id,
        action="REMITTANCE_COMPLETED",
        entity="transaction",
        entity_id=transaction.transaction_id,
        metadata={
            "previous_status": previous_status,
            "new_status": transaction.status,
            "delivery_method": transaction.delivery_method,
        },
    )
    record_remittance_event(db, transaction, "REMITTANCE_COMPLETED", current_user.id)
    db.commit()
    db.refresh(transaction)
    return get_transaction(db, transaction.id, current_user.id)


@router.get("/{transaction_id}", response_model=TransactionRead)
def read_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    link_received_transactions_by_email(db, current_user.id, current_user.email)
    db.commit()
    transaction = get_transaction(db, transaction_id, current_user.id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TRANSACTION_NOT_FOUND", "message": "Transaccion no encontrada"},
        )
    return transaction
