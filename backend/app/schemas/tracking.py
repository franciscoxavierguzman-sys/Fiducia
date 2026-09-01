from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class StatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    previous_status: str | None
    new_status: str
    changed_at: datetime
    changed_by: int | None
    reason: str | None


class RemittanceTrackingRead(BaseModel):
    remittance_number: str
    origin_country: str
    destination_country: str
    source_amount: Decimal
    source_currency: str
    destination_amount: Decimal
    destination_currency: str
    delivery_method: str
    status: str
    created_at: datetime
    timeline: list[StatusHistoryRead]
