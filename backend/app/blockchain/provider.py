from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session

from app.models.blockchain import BlockchainBlock


class BlockchainProvider(ABC):
    @abstractmethod
    def record_evidence(self, db: Session, evidence: dict[str, Any]) -> BlockchainBlock:
        raise NotImplementedError

    @abstractmethod
    def verify_evidence(self, db: Session, entity_reference: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_block(self, db: Session, block_index: int) -> BlockchainBlock | None:
        raise NotImplementedError

    @abstractmethod
    def get_chain(self, db: Session) -> list[BlockchainBlock]:
        raise NotImplementedError

    @abstractmethod
    def validate_chain(self, db: Session) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_entity_history(self, db: Session, entity_reference: str) -> list[BlockchainBlock]:
        raise NotImplementedError
