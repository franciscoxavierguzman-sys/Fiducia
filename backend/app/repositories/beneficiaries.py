from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.beneficiary import Beneficiary
from app.models.beneficiary_relationship import BeneficiaryRelationship
from app.models.department import Department
from app.models.municipality import Municipality
from app.repositories.users import get_user_by_email
from app.schemas.beneficiary import BeneficiaryCreate, BeneficiaryUpdate


def normalize_beneficiary_data(db: Session, data: dict) -> dict:
    if data.get("relationship_id") is not None:
        relationship = db.get(BeneficiaryRelationship, data["relationship_id"])
        if relationship is None or not relationship.is_active:
            raise ValueError("INVALID_RELATIONSHIP")
        data["relationship"] = relationship.name
        if relationship.name != "Otro":
            data["relationship_other"] = None

    if data.get("country") == "Guatemala":
        department_name = data.get("department")
        municipality_name = data.get("municipality")
        if not department_name or not municipality_name:
            raise ValueError("INVALID_GUATEMALA_LOCATION")
        department = db.scalar(select(Department).where(Department.name == department_name, Department.is_active.is_(True)))
        if department is None:
            raise ValueError("INVALID_GUATEMALA_LOCATION")
        municipality = db.scalar(
            select(Municipality).where(
                Municipality.department_id == department.id,
                Municipality.name == municipality_name,
                Municipality.is_active.is_(True),
            )
        )
        if municipality is None:
            raise ValueError("INVALID_GUATEMALA_LOCATION")
        data["city"] = None
    else:
        if not data.get("city"):
            raise ValueError("CITY_REQUIRED")
        data["department"] = data.get("department") or "N/A"
        data["municipality"] = data.get("municipality") or "N/A"
    return data


def list_beneficiaries(db: Session, sender_id: int) -> list[Beneficiary]:
    return list(
        db.scalars(
            select(Beneficiary)
            .where(Beneficiary.sender_id == sender_id)
            .order_by(Beneficiary.is_active.desc(), Beneficiary.created_at.desc())
        )
    )


def get_beneficiary(db: Session, beneficiary_id: int, sender_id: int) -> Beneficiary | None:
    beneficiary = db.get(Beneficiary, beneficiary_id)
    if beneficiary is None or beneficiary.sender_id != sender_id:
        return None
    return beneficiary


def create_beneficiary(db: Session, sender_id: int, payload: BeneficiaryCreate) -> Beneficiary:
    data = payload.model_dump()
    data = normalize_beneficiary_data(db, data)
    email = data.get("email")
    data["email"] = email.lower() if email else None
    linked_user = get_user_by_email(db, email) if email else None
    beneficiary = Beneficiary(sender_id=sender_id, beneficiary_user_id=linked_user.id if linked_user else None, **data)
    db.add(beneficiary)
    db.flush()
    return beneficiary


def update_beneficiary(db: Session, beneficiary: Beneficiary, payload: BeneficiaryUpdate) -> Beneficiary:
    data = payload.model_dump(exclude_unset=True)
    merged = {
        "country": beneficiary.country,
        "department": beneficiary.department,
        "municipality": beneficiary.municipality,
        "city": beneficiary.city,
        "relationship_id": beneficiary.relationship_id,
        "relationship": beneficiary.relationship,
        "relationship_other": beneficiary.relationship_other,
    }
    merged.update(data)
    data = normalize_beneficiary_data(db, merged)
    data = {field: value for field, value in data.items() if field in payload.model_dump(exclude_unset=True) or field in {"relationship", "relationship_other", "department", "municipality", "city"}}
    if "email" in data:
        email = data["email"]
        data["email"] = email.lower() if email else None
        linked_user = get_user_by_email(db, email) if email else None
        beneficiary.beneficiary_user_id = linked_user.id if linked_user else None
        for transaction in beneficiary.transactions:
            transaction.beneficiary_user_id = beneficiary.beneficiary_user_id
    for field, value in data.items():
        setattr(beneficiary, field, value)
    db.flush()
    return beneficiary
