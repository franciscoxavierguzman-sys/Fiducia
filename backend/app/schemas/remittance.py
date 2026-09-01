from decimal import Decimal

from pydantic import BaseModel, Field


class RemittanceSimulationRequest(BaseModel):
    beneficiary_id: int
    origin_country: str
    destination_country: str
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str
    funding_source_id: int | None = None
    payment_method: str
    delivery_method: str


class RemittanceCorridorRead(BaseModel):
    id: int
    origin_country: str
    destination_country: str
    origin_currency: str
    destination_currency: str
    min_amount: Decimal
    max_amount: Decimal
    estimated_delivery: str


class RemittanceSimulationResponse(BaseModel):
    beneficiary_id: int
    beneficiary_user_id: int | None
    origin_country: str
    destination_country: str
    source_amount: Decimal
    source_currency: str
    amount: Decimal
    currency: str
    commission_rate: Decimal
    commission_amount: Decimal
    total_amount: Decimal
    total_debit_amount: Decimal
    total_debit_currency: str
    exchange_rate: Decimal
    exchange_rate_source: str = "Tabla local"
    destination_currency: str
    destination_amount: Decimal
    payment_method: str
    delivery_method: str
    estimated_delivery: str
    is_exchange_rate_simulated: bool = True
