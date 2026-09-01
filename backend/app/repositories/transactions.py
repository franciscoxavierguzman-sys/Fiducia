from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, joinedload

from app.models.beneficiary import Beneficiary
from app.models.transaction import Transaction


def list_transactions(db: Session, sender_id: int) -> list[Transaction]:
    return list_sent_transactions(db, sender_id)


def list_sent_transactions(db: Session, sender_id: int) -> list[Transaction]:
    return list(
        db.scalars(
            select(Transaction)
            .options(joinedload(Transaction.beneficiary), joinedload(Transaction.sender))
            .where(Transaction.sender_id == sender_id)
            .order_by(Transaction.created_at.desc(), Transaction.id.desc())
        )
    )


def link_received_transactions_by_email(db: Session, beneficiary_user_id: int, email: str) -> None:
    normalized_email = email.lower()
    beneficiary_ids = select(Beneficiary.id).where(func.lower(Beneficiary.email) == normalized_email)
    db.execute(
        update(Beneficiary)
        .where(Beneficiary.id.in_(beneficiary_ids), Beneficiary.beneficiary_user_id.is_(None))
        .values(beneficiary_user_id=beneficiary_user_id)
    )
    db.execute(
        update(Transaction)
        .where(Transaction.beneficiary_id.in_(beneficiary_ids), Transaction.beneficiary_user_id.is_(None))
        .values(beneficiary_user_id=beneficiary_user_id)
    )
    db.flush()


def list_received_transactions(db: Session, beneficiary_user_id: int) -> list[Transaction]:
    return list(
        db.scalars(
            select(Transaction)
            .options(joinedload(Transaction.beneficiary), joinedload(Transaction.sender))
            .where(Transaction.beneficiary_user_id == beneficiary_user_id)
            .order_by(Transaction.created_at.desc(), Transaction.id.desc())
        )
    )


def get_transaction(db: Session, transaction_id: int, user_id: int) -> Transaction | None:
    transaction = db.scalar(
        select(Transaction)
        .options(joinedload(Transaction.beneficiary), joinedload(Transaction.sender))
        .where(
            Transaction.id == transaction_id,
            or_(Transaction.sender_id == user_id, Transaction.beneficiary_user_id == user_id),
        )
    )
    return transaction


def get_transaction_by_number(db: Session, remittance_number: str, user_id: int) -> Transaction | None:
    return db.scalar(
        select(Transaction)
        .options(
            joinedload(Transaction.beneficiary),
            joinedload(Transaction.sender),
            joinedload(Transaction.status_history),
        )
        .where(
            Transaction.transaction_id == remittance_number,
            or_(Transaction.sender_id == user_id, Transaction.beneficiary_user_id == user_id),
        )
    )


def get_received_transaction(db: Session, transaction_id: int, beneficiary_user_id: int) -> Transaction | None:
    return db.scalar(
        select(Transaction)
        .options(joinedload(Transaction.beneficiary), joinedload(Transaction.sender))
        .where(Transaction.id == transaction_id, Transaction.beneficiary_user_id == beneficiary_user_id)
    )
