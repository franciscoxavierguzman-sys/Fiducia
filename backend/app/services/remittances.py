from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.beneficiary import Beneficiary
from app.models.country import Country
from app.models.exchange_rate import ExchangeRate
from app.models.funding_source import FundingSource
from app.models.remittance_corridor import RemittanceCorridor
from app.schemas.remittance import RemittanceCorridorRead, RemittanceSimulationRequest, RemittanceSimulationResponse
from app.services.banguat import get_banguat_usd_gtq_rate

PAYMENT_METHODS = {"DEBIT_CARD", "BANK_TRANSFER", "DIGITAL_WALLET"}
DELIVERY_METHODS = {"BANK_DEPOSIT", "TRANSFER", "WALLET", "CASH_PICKUP"}
TRANSACTION_STATUSES = {
    "CREATED",
    "VALIDATING",
    "RISK_ANALYSIS",
    "APPROVED",
    "PROCESSING",
    "AVAILABLE",
    "COMPLETED",
    "REVIEW_REQUIRED",
    "REJECTED",
}

MONEY_QUANT = Decimal("0.01")
RATE_QUANT = Decimal("0.000001")


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def rate(value: Decimal) -> Decimal:
    return value.quantize(RATE_QUANT, rounding=ROUND_HALF_UP)


def decimal_setting(value: float) -> Decimal:
    return Decimal(str(value))


def get_owned_active_beneficiary(db: Session, beneficiary_id: int, sender_id: int) -> Beneficiary:
    beneficiary = db.get(Beneficiary, beneficiary_id)
    if beneficiary is None or beneficiary.sender_id != sender_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "BENEFICIARY_NOT_FOUND", "message": "Beneficiario no encontrado"},
        )
    if not beneficiary.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "BENEFICIARY_INACTIVE", "message": "El beneficiario esta inactivo"},
        )
    return beneficiary


def list_active_corridors(db: Session) -> list[RemittanceCorridorRead]:
    corridors = db.scalars(
        select(RemittanceCorridor)
        .join(Country, RemittanceCorridor.origin_country_id == Country.id)
        .where(RemittanceCorridor.is_active.is_(True))
        .order_by(RemittanceCorridor.id)
    ).all()
    return [
        RemittanceCorridorRead(
            id=corridor.id,
            origin_country=cast_country_name(db, corridor.origin_country_id),
            destination_country=cast_country_name(db, corridor.destination_country_id),
            origin_currency=corridor.origin_currency,
            destination_currency=corridor.destination_currency,
            min_amount=corridor.min_amount,
            max_amount=corridor.max_amount,
            estimated_delivery=corridor.estimated_delivery,
        )
        for corridor in corridors
    ]


def cast_country_name(db: Session, country_id: int) -> str:
    country = db.get(Country, country_id)
    return country.name if country else ""


def get_supported_corridor(db: Session, origin_country: str, destination_country: str) -> RemittanceCorridor:
    if origin_country == destination_country:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "SAME_COUNTRY_CORRIDOR", "message": "El origen y destino deben ser diferentes"},
        )

    origin = db.scalar(select(Country).where(Country.name == origin_country))
    destination = db.scalar(select(Country).where(Country.name == destination_country))
    if origin is None or destination is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_COUNTRY", "message": "Pais de origen o destino no permitido"},
        )

    if origin.name != "Guatemala" and destination.name != "Guatemala":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "UNSUPPORTED_CORRIDOR", "message": "FIDUCIA requiere que Guatemala sea origen o destino"},
        )

    corridor = db.scalar(
        select(RemittanceCorridor).where(
            RemittanceCorridor.origin_country_id == origin.id,
            RemittanceCorridor.destination_country_id == destination.id,
            RemittanceCorridor.is_active.is_(True),
        )
    )
    if corridor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "UNSUPPORTED_CORRIDOR", "message": "Corredor de remesa no disponible"},
        )
    return corridor


def can_pay_with_funding_currency(corridor: RemittanceCorridor, funding_currency: str) -> bool:
    if funding_currency == corridor.origin_currency:
        return True
    return corridor.origin_currency == "USD" and corridor.destination_currency == "GTQ" and funding_currency == "GTQ"


def validate_business_inputs(
    db: Session, payload: RemittanceSimulationRequest, sender_id: int
) -> tuple[Beneficiary, RemittanceCorridor, FundingSource | None]:
    corridor = get_supported_corridor(db, payload.origin_country, payload.destination_country)
    amount = money(payload.amount)
    minimum = money(Decimal(corridor.min_amount))
    maximum = money(Decimal(corridor.max_amount))
    if amount < minimum or amount > maximum:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "AMOUNT_OUT_OF_RANGE",
                "message": f"El monto debe estar entre {minimum} y {maximum}.",
            },
        )

    if payload.payment_method not in PAYMENT_METHODS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_PAYMENT_METHOD", "message": "Metodo de pago no permitido"},
        )

    if payload.delivery_method not in DELIVERY_METHODS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_DELIVERY_METHOD", "message": "Metodo de entrega no permitido"},
        )

    if payload.currency != corridor.origin_currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CURRENCY",
                "message": f"La moneda de origen para este corredor es {corridor.origin_currency}",
            },
        )

    funding_source = None
    if payload.funding_source_id is not None:
        funding_source = db.get(FundingSource, payload.funding_source_id)
        if (
            funding_source is None
            or funding_source.user_id != sender_id
            or not funding_source.is_active
            or not can_pay_with_funding_currency(corridor, funding_source.currency)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_FUNDING_SOURCE", "message": "Metodo de pago no disponible para esta remesa"},
            )

    beneficiary = get_owned_active_beneficiary(db, payload.beneficiary_id, sender_id)
    if beneficiary.country != payload.destination_country or beneficiary.currency != corridor.destination_currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INCOMPATIBLE_BENEFICIARY",
                "message": "El beneficiario no corresponde al pais destino del corredor seleccionado",
            },
        )
    return beneficiary, corridor, funding_source


def get_exchange_rate(db: Session, source_currency: str, destination_currency: str) -> ExchangeRate:
    exchange_rate = db.scalars(
        select(ExchangeRate)
        .where(
            ExchangeRate.source_currency == source_currency,
            ExchangeRate.destination_currency == destination_currency,
        )
        .order_by(ExchangeRate.effective_date.desc(), ExchangeRate.id.desc())
    ).first()
    if exchange_rate is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EXCHANGE_RATE_NOT_FOUND", "message": "Tipo de cambio no disponible"},
        )
    return exchange_rate


def resolve_exchange_rate(db: Session, corridor: RemittanceCorridor) -> tuple[Decimal, bool, str]:
    if corridor.destination_currency == "GTQ" and corridor.origin_currency == "USD":
        try:
            return rate(get_banguat_usd_gtq_rate()), False, "Banco de Guatemala"
        except Exception:
            pass
    exchange = get_exchange_rate(db, corridor.origin_currency, corridor.destination_currency)
    return rate(Decimal(exchange.rate)), exchange.is_simulated, "Tabla local"


def simulate_remittance(db: Session, payload: RemittanceSimulationRequest, sender_id: int) -> RemittanceSimulationResponse:
    beneficiary, corridor, funding_source = validate_business_inputs(db, payload, sender_id)
    exchange_rate, is_exchange_rate_simulated, exchange_rate_source = resolve_exchange_rate(db, corridor)
    amount = money(payload.amount)
    commission_rate = rate(decimal_setting(settings.commission_rate))
    commission_amount = money(amount * commission_rate)
    total_amount = money(amount + commission_amount)
    total_debit_currency = funding_source.currency if funding_source is not None else corridor.origin_currency
    total_debit_amount = total_amount
    if total_debit_currency == corridor.destination_currency and corridor.origin_currency == "USD" and corridor.destination_currency == "GTQ":
        total_debit_amount = money(total_amount * exchange_rate)
    destination_amount = money(amount * exchange_rate)

    return RemittanceSimulationResponse(
        beneficiary_id=payload.beneficiary_id,
        beneficiary_user_id=beneficiary.beneficiary_user_id,
        origin_country=payload.origin_country,
        destination_country=payload.destination_country,
        source_amount=amount,
        source_currency=corridor.origin_currency,
        amount=amount,
        currency=corridor.origin_currency,
        commission_rate=commission_rate,
        commission_amount=commission_amount,
        total_amount=total_amount,
        total_debit_amount=total_debit_amount,
        total_debit_currency=total_debit_currency,
        exchange_rate=exchange_rate,
        exchange_rate_source=exchange_rate_source,
        destination_currency=corridor.destination_currency,
        destination_amount=destination_amount,
        payment_method=payload.payment_method,
        delivery_method=payload.delivery_method,
        estimated_delivery=corridor.estimated_delivery,
        is_exchange_rate_simulated=is_exchange_rate_simulated,
    )
