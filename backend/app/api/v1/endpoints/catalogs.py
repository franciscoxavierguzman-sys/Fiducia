from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.beneficiary_relationship import BeneficiaryRelationship
from app.models.country import Country
from app.models.department import Department
from app.models.municipality import Municipality
from app.schemas.catalog import BeneficiaryRelationshipRead, CountryRead, DepartmentRead, MunicipalityRead

router = APIRouter()


@router.get("/countries", response_model=list[CountryRead])
def countries(db: Session = Depends(get_db)):
    return list(db.scalars(select(Country).where(Country.is_destination_enabled.is_(True)).order_by(Country.name)))


@router.get("/beneficiary-relationships", response_model=list[BeneficiaryRelationshipRead])
def beneficiary_relationships(db: Session = Depends(get_db)):
    return list(
        db.scalars(
            select(BeneficiaryRelationship)
            .where(BeneficiaryRelationship.is_active.is_(True))
            .order_by(BeneficiaryRelationship.id)
        )
    )


@router.get("/departments", response_model=list[DepartmentRead])
def departments(db: Session = Depends(get_db)):
    return list(db.scalars(select(Department).where(Department.is_active.is_(True)).order_by(Department.name)))


@router.get("/departments/{department_id}/municipalities", response_model=list[MunicipalityRead])
def municipalities(department_id: int, db: Session = Depends(get_db)):
    return list(
        db.scalars(
            select(Municipality)
            .where(Municipality.department_id == department_id, Municipality.is_active.is_(True))
            .order_by(Municipality.name)
        )
    )
