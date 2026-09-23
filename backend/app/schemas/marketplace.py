from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MarketplaceProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    description: str
    category: str
    price_amount: Decimal
    currency: str
    stock: int
    image_url: str | None
    is_active: bool


class MarketplaceOrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=20)


class MarketplaceOrderCreate(BaseModel):
    remittance_transaction_id: int
    items: list[MarketplaceOrderItemCreate]

    @model_validator(mode="after")
    def validate_items(self) -> "MarketplaceOrderCreate":
        if not self.items:
            raise ValueError("order must include at least one item")
        return self


class MarketplaceOrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price_amount: Decimal
    total_amount: Decimal
    product: MarketplaceProductRead


class MarketplaceOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    buyer_id: int
    remittance_transaction_id: int
    status: str
    subtotal_amount: Decimal
    total_amount: Decimal
    currency: str
    created_at: datetime
    items: list[MarketplaceOrderItemRead]


class MarketplaceRemittanceBalanceRead(BaseModel):
    transaction_id: int
    remittance_number: str
    currency: str
    original_amount: Decimal
    spent_amount: Decimal
    available_amount: Decimal
    completed_at: datetime
