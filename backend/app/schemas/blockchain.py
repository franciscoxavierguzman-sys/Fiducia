from pydantic import BaseModel


class BlockchainBlockRead(BaseModel):
    block_index: int
    timestamp: str
    event_type: str
    entity_type: str
    entity_reference: str
    evidence_hash: str
    previous_hash: str
    nonce: int
    difficulty: int
    block_hash: str
    schema_version: str
    record_status: str
    mining_time_ms: int

    model_config = {"from_attributes": True}


class BlockchainInfo(BaseModel):
    blockchain_engine_version: str
    hash_algorithm: str
    difficulty: int
    total_blocks: int
    total_evidence: int
    genesis_hash: str | None
    last_block_hash: str | None
    chain_valid: bool
    supported_schema_versions: list[str]


class ChainValidationResult(BaseModel):
    valid: bool
    blocks_checked: int
    errors: list[dict]


class EvidenceVerificationResult(BaseModel):
    status: str
    verified: int
    mismatches: list[dict]


class BlockchainMetrics(BaseModel):
    total_blocks: int
    total_evidence: int
    blocks_by_event_type: dict[str, int]
    chain_valid: bool
    last_block_timestamp: str | None
    average_mining_time_ms: float | None
