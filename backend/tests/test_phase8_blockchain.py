from datetime import UTC, datetime
from decimal import Decimal

from app.blockchain.canonical import canonical_json
from app.blockchain.config import DEFAULT_DIFFICULTY
from app.blockchain.evidence import remittance_evidence, risk_evidence
from app.blockchain.hash import hash_payload, is_sha256_hex
from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.models.blockchain import BlockchainBlock
from app.models.risk_assessment import RiskAssessment
from app.models.transaction import Transaction


def register_and_login(client, email: str, role: str = "CLIENT"):
    payload = {
        "first_name": "Chain",
        "last_name": "User",
        "email": email,
        "phone": "55551234",
        "country": "Guatemala",
        "password": "Password123",
        "confirm_password": "Password123",
        "terms_accepted": True,
        "human_check_accepted": True,
        "document_type": "DPI",
        "fictitious_document_id": "1234567890123",
        "birth_date": "1995-05-15",
        "role": role,
    }
    user = client.post("/api/v1/auth/register", json=payload).json()
    token = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123"}).json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


def create_beneficiary(client, headers, email: str = "chain-beneficiary@example.com"):
    response = client.post(
        "/api/v1/beneficiaries",
        headers=headers,
        json={
            "first_name": "Javier",
            "last_name": "Guzman",
            "email": email,
            "relationship": "Amigo / Amiga",
            "country": "Guatemala",
            "currency": "GTQ",
            "department": "Guatemala",
            "municipality": "Guatemala",
            "delivery_method": "BANK_DEPOSIT",
            "bank_name": "Banco Industrial, S.A.",
            "account_type": "Ahorro",
            "account_last_four": "1234",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_remittance(client, headers, beneficiary_id: int):
    response = client.post(
        "/api/v1/transactions",
        headers=headers,
        json={
            "beneficiary_id": beneficiary_id,
            "origin_country": "Estados Unidos",
            "destination_country": "Guatemala",
            "amount": "400.00",
            "currency": "USD",
            "payment_method": "BANK_TRANSFER",
            "delivery_method": "BANK_DEPOSIT",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_canonicalization_hash_decimal_and_timestamp_are_deterministic():
    instant = datetime(2026, 1, 1, 6, 0, tzinfo=UTC)
    left = {"b": Decimal("100.00"), "a": instant}
    right = {"a": "2026-01-01T06:00:00Z", "b": 100.0}

    assert canonical_json(left) == canonical_json(right)
    assert hash_payload(left) == hash_payload(right)
    assert is_sha256_hex(hash_payload(left))


def test_blockchain_records_genesis_pow_and_domain_events(client):
    _, headers = register_and_login(client, "chain-sender@example.com")
    beneficiary = create_beneficiary(client, headers)
    transaction = create_remittance(client, headers, beneficiary["id"])

    with SessionLocal() as db:
        blocks = db.query(BlockchainBlock).order_by(BlockchainBlock.block_index).all()
        assert blocks[0].event_type == "GENESIS"
        assert blocks[0].previous_hash == "0" * 64
        assert len(blocks) == 4
        assert [block.block_index for block in blocks] == [0, 1, 2, 3]
        assert all(block.block_hash.startswith("0" * DEFAULT_DIFFICULTY) for block in blocks)
        assert blocks[1].event_type == "REMITTANCE_CREATED"
        assert blocks[2].event_type == "REMITTANCE_AVAILABLE"
        assert blocks[3].event_type == "RISK_ASSESSMENT_RECORDED"
        assert all(blocks[index].previous_hash == blocks[index - 1].block_hash for index in range(1, len(blocks)))
        assert db.query(BlockchainBlock).filter(BlockchainBlock.entity_reference == str(transaction["id"])).count() == 3


def test_blockchain_idempotency_and_privacy(client):
    _, headers = register_and_login(client, "privacy-sender@example.com")
    beneficiary = create_beneficiary(client, headers, email="privacy-beneficiary@example.com")
    transaction = create_remittance(client, headers, beneficiary["id"])

    with SessionLocal() as db:
        from app.blockchain.local_provider import local_blockchain_provider
        from app.models.transaction import Transaction

        saved = db.get(Transaction, transaction["id"])
        first = local_blockchain_provider.record_evidence(db, remittance_evidence(saved, "REMITTANCE_CREATED", saved.created_at, "AVAILABLE"))
        second = local_blockchain_provider.record_evidence(db, remittance_evidence(saved, "REMITTANCE_CREATED", saved.created_at, "AVAILABLE"))
        assert first.id == second.id
        for block in db.query(BlockchainBlock).all():
            serialized = " ".join(str(getattr(block, field)) for field in ["event_type", "entity_type", "entity_reference", "evidence_hash", "block_hash"])
            assert "privacy-beneficiary@example.com" not in serialized
            assert "55551234" not in serialized
            assert "Banco Industrial" not in serialized
            assert "1234567890123" not in serialized


def test_remittance_event_idempotency_records_one_evidence(client):
    _, headers = register_and_login(client, "remittance-idempotency@example.com")
    beneficiary = create_beneficiary(client, headers, email="remittance-idempotency-beneficiary@example.com")
    transaction = create_remittance(client, headers, beneficiary["id"])

    with SessionLocal() as db:
        from app.blockchain.local_provider import local_blockchain_provider

        saved = db.get(Transaction, transaction["id"])
        before = db.query(BlockchainBlock).count()
        first = local_blockchain_provider.record_evidence(db, remittance_evidence(saved, "REMITTANCE_CREATED", saved.created_at, "AVAILABLE"))
        second = local_blockchain_provider.record_evidence(db, remittance_evidence(saved, "REMITTANCE_CREATED", saved.created_at, "AVAILABLE"))
        after = db.query(BlockchainBlock).count()

        assert first.id == second.id
        assert first.idempotency_key == second.idempotency_key
        assert after == before


def test_risk_assessment_idempotency_uses_assessment_identity(client):
    _, headers = register_and_login(client, "risk-idempotency@example.com")
    beneficiary = create_beneficiary(client, headers, email="risk-idempotency-beneficiary@example.com")
    transaction = create_remittance(client, headers, beneficiary["id"])

    with SessionLocal() as db:
        from app.blockchain.local_provider import local_blockchain_provider

        assessment_a = db.query(RiskAssessment).filter(RiskAssessment.remittance_id == transaction["id"]).one()
        before = db.query(BlockchainBlock).filter(BlockchainBlock.entity_type == "risk_assessment", BlockchainBlock.entity_reference == str(transaction["id"])).count()
        first = local_blockchain_provider.record_evidence(db, risk_evidence(assessment_a))
        second = local_blockchain_provider.record_evidence(db, risk_evidence(assessment_a))
        after_same = db.query(BlockchainBlock).filter(BlockchainBlock.entity_type == "risk_assessment", BlockchainBlock.entity_reference == str(transaction["id"])).count()

        assessment_b = RiskAssessment(
            remittance_id=transaction["id"],
            assessment_sequence=2,
            rule_score=Decimal("35.00"),
            rules_version="rules-v1",
            triggered_rules_json=[],
            ml_probability=Decimal("0.250000"),
            ml_model_version="fraud-model-v1",
            ml_threshold=Decimal("0.2500"),
            anomaly_score=Decimal("12.00"),
            anomaly_model_version="anomaly-model-v1",
            final_risk_score=Decimal("28.50"),
            risk_band="MEDIUM",
            recommended_action="REVIEW",
            risk_engine_version="risk-engine-v1.1",
            weights_json={"rules": 0.3, "ml": 0.5, "anomaly": 0.2},
            risk_band_thresholds_json={"medium": 25, "high": 40},
            signal_status_json={"rules": "available", "ml": "available", "anomaly": "available"},
            explanations_json=["Synthetic second assessment for blockchain idempotency test."],
        )
        db.add(assessment_b)
        db.flush()
        third = local_blockchain_provider.record_evidence(db, risk_evidence(assessment_b))
        after_distinct = db.query(BlockchainBlock).filter(BlockchainBlock.entity_type == "risk_assessment", BlockchainBlock.entity_reference == str(transaction["id"])).count()

        assert before == 1
        assert first.id == second.id
        assert first.idempotency_key == second.idempotency_key
        assert after_same == 1
        assert after_distinct == 2
        assert third.id != first.id
        assert third.idempotency_key != first.idempotency_key
        assert third.evidence_hash != first.evidence_hash
        assert third.block_index != first.block_index


def test_chain_validation_tampering_and_evidence_verification(client):
    _, sender_headers = register_and_login(client, "verify-sender@example.com")
    receiver, receiver_headers = register_and_login(client, "verify-receiver@example.com")
    _, admin_headers = register_and_login(client, "verify-admin@example.com", role="ADMIN")
    beneficiary = create_beneficiary(client, sender_headers, email=receiver["email"])
    transaction = create_remittance(client, sender_headers, beneficiary["id"])

    received = client.post(f"/api/v1/transactions/{transaction['id']}/receive", headers=receiver_headers)
    assert received.status_code == 200

    validation = client.get("/api/v1/blockchain/validate", headers=admin_headers)
    assert validation.status_code == 200
    assert validation.json()["valid"] is True

    verification = client.get(f"/api/v1/blockchain/verify/{transaction['id']}", headers=admin_headers)
    assert verification.status_code == 200
    assert verification.json()["status"] == "VERIFIED"

    with SessionLocal() as db:
        block = db.query(BlockchainBlock).filter(BlockchainBlock.block_index == 3).one()
        block.evidence_hash = "f" * 64
        db.commit()

    tampered = client.get("/api/v1/blockchain/validate", headers=admin_headers)
    assert tampered.status_code == 200
    assert tampered.json()["valid"] is False
    assert any(error["block_index"] == 3 for error in tampered.json()["errors"])


def test_blockchain_permissions_and_safe_client_traceability(client):
    _, sender_headers = register_and_login(client, "chain-client@example.com")
    _, other_headers = register_and_login(client, "chain-other@example.com")
    _, analyst_headers = register_and_login(client, "chain-analyst@example.com", role="RISK_ANALYST")
    _, admin_headers = register_and_login(client, "chain-admin@example.com", role="ADMIN")
    beneficiary = create_beneficiary(client, sender_headers)
    transaction = create_remittance(client, sender_headers, beneficiary["id"])

    client_blocks = client.get("/api/v1/blockchain/blocks", headers=sender_headers)
    assert client_blocks.status_code == 403

    analyst_blocks = client.get("/api/v1/blockchain/blocks", headers=analyst_headers)
    assert analyst_blocks.status_code == 200

    client_overview = client.get("/api/v1/blockchain/overview", headers=sender_headers)
    assert client_overview.status_code == 403

    analyst_overview = client.get("/api/v1/blockchain/overview", headers=analyst_headers)
    assert analyst_overview.status_code == 200
    overview = analyst_overview.json()
    assert overview["info"]["chain_valid"] is True
    assert overview["metrics"]["total_blocks"] >= 1
    assert len(overview["blocks"]) >= 1

    admin_validate = client.get("/api/v1/blockchain/validate", headers=admin_headers)
    assert admin_validate.status_code == 200

    analyst_validate = client.get("/api/v1/blockchain/validate", headers=analyst_headers)
    assert analyst_validate.status_code == 403
    assert analyst_validate.json()["detail"]["code"] == "BLOCKCHAIN_ADMIN_REQUIRED"

    own_history = client.get(f"/api/v1/blockchain/transactions/{transaction['id']}/history", headers=sender_headers)
    assert own_history.status_code == 200
    assert len(own_history.json()) == 3

    other_history = client.get(f"/api/v1/blockchain/transactions/{transaction['id']}/history", headers=other_headers)
    assert other_history.status_code == 404


def test_blockchain_backfill_records_legacy_remittances(client):
    from app.services.blockchain import backfill_blockchain_evidence

    _, headers = register_and_login(client, "backfill-sender@example.com")
    beneficiary = create_beneficiary(client, headers, email="backfill-beneficiary@example.com")
    transaction = create_remittance(client, headers, beneficiary["id"])

    with SessionLocal() as db:
        db.query(BlockchainBlock).delete()
        db.commit()

    missing = client.get(f"/api/v1/blockchain/verify/{transaction['id']}", headers=headers)
    assert missing.status_code == 200
    assert missing.json()["status"] == "NOT_FOUND"

    with SessionLocal() as db:
        result = backfill_blockchain_evidence(db)
        db.commit()

    assert result["transactions_scanned"] == 1
    assert result["blocks_created"] >= 4

    verified = client.get(f"/api/v1/blockchain/verify/{transaction['id']}", headers=headers)
    assert verified.status_code == 200
    assert verified.json()["status"] == "VERIFIED"


def test_blockchain_failure_does_not_break_remittance_flow(client, monkeypatch):
    from app.services import blockchain as blockchain_service

    def fail_record_evidence(db, evidence):
        raise RuntimeError("simulated blockchain outage")

    monkeypatch.setattr(blockchain_service.local_blockchain_provider, "record_evidence", fail_record_evidence)

    _, headers = register_and_login(client, "failure-sender@example.com")
    beneficiary = create_beneficiary(client, headers, email="failure-beneficiary@example.com")
    transaction = create_remittance(client, headers, beneficiary["id"])

    with SessionLocal() as db:
        saved = db.get(Transaction, transaction["id"])
        assessment = db.query(RiskAssessment).filter(RiskAssessment.remittance_id == transaction["id"]).one_or_none()
        failed_events = db.query(AuditLog).filter(AuditLog.action == "BLOCKCHAIN_EVIDENCE_FAILED").all()

        assert saved is not None
        assert saved.status == "AVAILABLE"
        assert assessment is not None
        assert assessment.risk_engine_version == "risk-engine-v1.1"
        assert len(failed_events) >= 2
        assert db.query(BlockchainBlock).count() == 0
