from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.blockchain.integrity import latest_integrity_status, verify_blockchain_integrity, verify_transaction_integrity
from app.schemas.blockchain import (
    BlockchainBlockRead,
    BlockchainInfo,
    BlockchainIntegrityResult,
    BlockchainIntegritySummary,
    BlockchainMetrics,
    BlockchainOverview,
    ChainValidationResult,
    EvidenceVerificationResult,
)
from app.services.blockchain import (
    blockchain_info,
    blockchain_metrics,
    get_block_by_index,
    list_blocks,
    transaction_history,
    validate_blockchain,
    verify_transaction_evidence,
)

router = APIRouter()


def require_blockchain_audit_access(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name not in {"ADMIN", "RISK_ANALYST"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "BLOCKCHAIN_FORBIDDEN", "message": "Acceso blockchain no autorizado"})
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "BLOCKCHAIN_ADMIN_REQUIRED", "message": "Operacion disponible solo para administrador"})
    return current_user


@router.get("/info", response_model=BlockchainInfo)
def read_blockchain_info(_: User = Depends(require_blockchain_audit_access), db: Session = Depends(get_db)) -> dict:
    return blockchain_info(db)


@router.get("/metrics", response_model=BlockchainMetrics)
def read_blockchain_metrics(_: User = Depends(require_blockchain_audit_access), db: Session = Depends(get_db)) -> dict:
    return blockchain_metrics(db)


@router.get("/overview", response_model=BlockchainOverview)
def read_blockchain_overview(_: User = Depends(require_blockchain_audit_access), db: Session = Depends(get_db)) -> dict:
    return {
        "info": blockchain_info(db),
        "metrics": blockchain_metrics(db),
        "blocks": list_blocks(db),
    }


@router.get("/blocks", response_model=list[BlockchainBlockRead])
def read_blocks(_: User = Depends(require_blockchain_audit_access), db: Session = Depends(get_db)) -> list:
    return list_blocks(db)


@router.get("/blocks/{block_index}", response_model=BlockchainBlockRead)
def read_block(block_index: int, _: User = Depends(require_blockchain_audit_access), db: Session = Depends(get_db)):
    block = get_block_by_index(db, block_index)
    if block is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "BLOCK_NOT_FOUND", "message": "Bloque no encontrado"})
    return block


@router.get("/transactions/{remittance_id}/history", response_model=list[BlockchainBlockRead])
def read_transaction_history(remittance_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list:
    if current_user.role.name == "CLIENT":
        from app.repositories.transactions import get_transaction

        if get_transaction(db, remittance_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "TRANSACTION_NOT_FOUND", "message": "Remesa no encontrada"})
    elif current_user.role.name not in {"ADMIN", "RISK_ANALYST"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "BLOCKCHAIN_FORBIDDEN", "message": "Acceso blockchain no autorizado"})
    return transaction_history(db, remittance_id)


@router.get("/verify/{remittance_id}", response_model=EvidenceVerificationResult)
def verify_transaction(remittance_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if current_user.role.name == "CLIENT":
        from app.repositories.transactions import get_transaction

        if get_transaction(db, remittance_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "TRANSACTION_NOT_FOUND", "message": "Remesa no encontrada"})
    elif current_user.role.name not in {"ADMIN", "RISK_ANALYST"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "BLOCKCHAIN_FORBIDDEN", "message": "Acceso blockchain no autorizado"})
    return verify_transaction_evidence(db, remittance_id)


@router.get("/validate", response_model=ChainValidationResult)
def validate_chain(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return validate_blockchain(db)


@router.get("/integrity/transactions/{remittance_id}", response_model=BlockchainIntegrityResult)
def verify_remittance_integrity(remittance_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if current_user.role.name == "CLIENT":
        from app.repositories.transactions import get_transaction

        if get_transaction(db, remittance_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "TRANSACTION_NOT_FOUND", "message": "Remesa no encontrada"})
    elif current_user.role.name not in {"ADMIN", "RISK_ANALYST"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "BLOCKCHAIN_FORBIDDEN", "message": "Acceso blockchain no autorizado"})
    return verify_transaction_integrity(db, remittance_id, actor_user_id=current_user.id, verification_source="API")


@router.post("/integrity/verify", response_model=BlockchainIntegritySummary)
def run_integrity_verification(current_user: User = Depends(require_blockchain_audit_access), db: Session = Depends(get_db)) -> dict:
    return verify_blockchain_integrity(db, actor_user_id=current_user.id, verification_source="API")


@router.get("/integrity/status", response_model=BlockchainIntegritySummary)
def read_integrity_status(_: User = Depends(require_blockchain_audit_access), db: Session = Depends(get_db)) -> dict:
    return latest_integrity_status(db)
