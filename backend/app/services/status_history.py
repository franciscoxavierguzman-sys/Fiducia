from sqlalchemy.orm import Session

from app.models.remittance_status_history import RemittanceStatusHistory
from app.models.transaction import Transaction


def record_status_change(
    db: Session,
    transaction: Transaction,
    *,
    previous_status: str | None,
    new_status: str,
    changed_by: int | None,
    reason: str | None = None,
) -> None:
    db.add(
        RemittanceStatusHistory(
            transaction_id=transaction.id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            reason=reason,
        )
    )
