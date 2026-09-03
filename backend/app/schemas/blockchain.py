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


class BlockchainOverview(BaseModel):
    info: BlockchainInfo
    metrics: BlockchainMetrics
    blocks: list[BlockchainBlockRead]


class BlockchainIntegrityResult(BaseModel):
    transaction_id: str
    remittance_number: str | None = None
    status: str
    stored_hash: str | None = None
    calculated_hash: str | None = None
    verified_at: str
    blockchain_reference: str | None = None
    details: str | None = None
    differences: list[dict] = []
    blocks_checked: int = 0
    verified_blocks: int | None = None
    mismatches: list[dict] = []


class BlockchainIntegritySummary(BaseModel):
    status: str
    verified_at: str
    total_transactions: int
    verified: int
    integrity_mismatches: int
    blockchain_record_missing: int
    database_record_missing: int
    legacy_not_protected: int
    chain_broken: int
    verification_errors: int
    chain_validation: ChainValidationResult
    results: list[BlockchainIntegrityResult] = []
