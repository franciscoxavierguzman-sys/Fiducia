from datetime import date
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.beneficiary_relationship import BeneficiaryRelationship
from app.models.country import Country
from app.models.department import Department
from app.models.exchange_rate import ExchangeRate
from app.models.municipality import Municipality
from app.models.remittance_corridor import RemittanceCorridor
from app.models.remittance_status_history import RemittanceStatusHistory
from app.models.role import Role
from app.models.transaction import Transaction


DEFAULT_ROLES = [
    ("CLIENT", "Cliente FIDUCIA"),
    ("RISK_ANALYST", "Analista de riesgos"),
    ("ADMIN", "Administrador"),
]

DEFAULT_COUNTRIES = [
    ("Estados Unidos", "USA", "USD", "Dolar estadounidense", "$", True, True),
    ("Canada", "CAN", "CAD", "Dolar canadiense", "$", True, True),
    ("Mexico", "MEX", "MXN", "Peso mexicano", "$", True, True),
    ("Espana", "ESP", "EUR", "Euro", "EUR", True, True),
    ("Guatemala", "GTM", "GTQ", "Quetzal guatemalteco", "Q", True, True),
]

DEFAULT_RELATIONSHIPS = [
    "Conyuge",
    "Padre / Madre",
    "Hijo / Hija",
    "Hermano / Hermana",
    "Abuelo / Abuela",
    "Nieto / Nieta",
    "Tio / Tia",
    "Primo / Prima",
    "Pareja",
    "Amigo / Amiga",
    "Socio comercial",
    "Otro",
]

DEFAULT_GUATEMALA_DEPARTMENTS = {
    "Guatemala": ["Guatemala", "Mixco", "Villa Nueva"],
    "Sacatepequez": ["Antigua Guatemala", "Ciudad Vieja", "Jocotenango"],
    "Quetzaltenango": ["Quetzaltenango", "Coatepeque", "Olintepeque"],
    "Escuintla": ["Escuintla", "Santa Lucia Cotzumalguapa", "Palin"],
}

DEFAULT_EXCHANGE_RATES = [
    ("USD", "GTQ", "7.80"),
    ("GTQ", "USD", "0.128205"),
    ("CAD", "GTQ", "5.75"),
    ("GTQ", "CAD", "0.173913"),
    ("MXN", "GTQ", "0.46"),
    ("GTQ", "MXN", "2.173913"),
    ("EUR", "GTQ", "8.50"),
    ("GTQ", "EUR", "0.117647"),
]


def seed_default_roles() -> None:
    db = SessionLocal()
    try:
        legacy_sender = db.scalar(select(Role).where(Role.name == "sender"))
        if legacy_sender is not None:
            legacy_sender.name = "CLIENT"
            legacy_sender.description = "Cliente FIDUCIA"
        legacy_risk = db.scalar(select(Role).where(Role.name == "risk_analyst"))
        if legacy_risk is not None:
            legacy_risk.name = "RISK_ANALYST"
        legacy_admin = db.scalar(select(Role).where(Role.name == "admin"))
        if legacy_admin is not None:
            legacy_admin.name = "ADMIN"

        for name, description in DEFAULT_ROLES:
            exists = db.scalar(select(Role).where(Role.name == name))
            if exists is None:
                db.add(Role(name=name, description=description))

        for name, iso_code, currency_code, currency_name, currency_symbol, is_origin_enabled, is_destination_enabled in DEFAULT_COUNTRIES:
            exists = db.scalar(select(Country).where(Country.name == name))
            if exists is None:
                db.add(
                    Country(
                        name=name,
                        iso_code=iso_code,
                        currency_code=currency_code,
                        currency_name=currency_name,
                        currency_symbol=currency_symbol,
                        is_origin_enabled=is_origin_enabled,
                        is_destination_enabled=is_destination_enabled,
                    )
                )
            else:
                exists.currency_name = currency_name
                exists.currency_symbol = currency_symbol

        for relationship in DEFAULT_RELATIONSHIPS:
            exists = db.scalar(select(BeneficiaryRelationship).where(BeneficiaryRelationship.name == relationship))
            if exists is None:
                db.add(BeneficiaryRelationship(name=relationship))

        for department_name, municipality_names in DEFAULT_GUATEMALA_DEPARTMENTS.items():
            department = db.scalar(select(Department).where(Department.name == department_name))
            if department is None:
                department = Department(name=department_name)
                db.add(department)
                db.flush()
            for municipality_name in municipality_names:
                exists = db.scalar(
                    select(Municipality).where(
                        Municipality.department_id == department.id,
                        Municipality.name == municipality_name,
                    )
                )
                if exists is None:
                    db.add(Municipality(department_id=department.id, name=municipality_name))

        db.flush()
        countries = {country.name: country for country in db.scalars(select(Country))}
        for source_currency, destination_currency, value in DEFAULT_EXCHANGE_RATES:
            exchange_exists = db.scalar(
                select(ExchangeRate).where(
                    ExchangeRate.source_currency == source_currency,
                    ExchangeRate.destination_currency == destination_currency,
                )
            )
            if exchange_exists is None:
                db.add(
                    ExchangeRate(
                        source_currency=source_currency,
                        destination_currency=destination_currency,
                        rate=Decimal(value),
                        source="simulated_seed",
                        is_simulated=True,
                        effective_date=date.today(),
                    )
                )

        for origin_name, destination_name in [
            ("Estados Unidos", "Guatemala"),
            ("Guatemala", "Estados Unidos"),
            ("Canada", "Guatemala"),
            ("Guatemala", "Canada"),
            ("Mexico", "Guatemala"),
            ("Guatemala", "Mexico"),
            ("Espana", "Guatemala"),
            ("Guatemala", "Espana"),
        ]:
            origin = countries[origin_name]
            destination = countries[destination_name]
            exists = db.scalar(
                select(RemittanceCorridor).where(
                    RemittanceCorridor.origin_country_id == origin.id,
                    RemittanceCorridor.destination_country_id == destination.id,
                )
            )
            if exists is None:
                db.add(
                    RemittanceCorridor(
                        origin_country_id=origin.id,
                        destination_country_id=destination.id,
                        origin_currency=origin.currency_code,
                        destination_currency=destination.currency_code,
                        min_amount=Decimal("10.00"),
                        max_amount=Decimal("5000.00"),
                        estimated_delivery="Disponible en minutos",
                    )
                )

        for transaction in db.scalars(select(Transaction)):
            if transaction.remittance_uuid is None:
                transaction.remittance_uuid = str(uuid4())
            history_exists = db.scalar(
                select(RemittanceStatusHistory).where(RemittanceStatusHistory.transaction_id == transaction.id)
            )
            if history_exists is None:
                db.add(
                    RemittanceStatusHistory(
                        transaction_id=transaction.id,
                        previous_status=None,
                        new_status=transaction.status,
                        changed_by=transaction.sender_id,
                        reason="LEGACY_BACKFILL",
                    )
                )
        db.commit()
    finally:
        db.close()
