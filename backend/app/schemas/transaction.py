from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, computed_field

from app.schemas.beneficiary import BeneficiaryRead
from app.schemas.user import UserRead
from app.schemas.remittance import RemittanceSimulationRequest


class TransactionCreate(RemittanceSimulationRequest):
    pass


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: str
    remittance_uuid: str | None
    sender_id: int
    beneficiary_id: int
    beneficiary_user_id: int | None
    funding_source_id: int | None
    origin_country: str
    destination_country: str
    source_amount: Decimal
    source_currency: str
    amount: Decimal
    currency: str
    exchange_rate: Decimal
    commission_rate: Decimal
    commission_amount: Decimal
    total_amount: Decimal
    debit_amount: Decimal | None
    debit_currency: str | None
    destination_amount: Decimal
    payment_method: str
    delivery_method: str
    status: str
    rule_score: Decimal | None
    ml_probability: Decimal | None
    anomaly_score: Decimal | None
    final_risk_score: Decimal | None
    risk_level: str | None
    model_version: str | None
    created_at: datetime
    updated_at: datetime
    beneficiary: BeneficiaryRead
    sender: UserRead

    @computed_field
    @property
    def remittance_number(self) -> str:
        return self.transaction_id

    @computed_field
    @property
    def total_debit_amount(self) -> Decimal:
        return self.debit_amount or self.total_amount

    @computed_field
    @property
    def total_debit_currency(self) -> str:
        return self.debit_currency or self.currency
