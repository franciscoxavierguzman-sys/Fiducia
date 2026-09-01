from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BeneficiaryBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    relationship: str = Field(min_length=1, max_length=100)
    relationship_id: int | None = None
    relationship_other: str | None = Field(default=None, max_length=120)
    country: str = Field(default="Guatemala", min_length=2, max_length=100)
    currency: str = Field(default="GTQ", min_length=3, max_length=3)
    city: str | None = Field(default=None, max_length=120)
    department: str | None = Field(default=None, max_length=100)
    municipality: str | None = Field(default=None, max_length=100)
    delivery_method: str = Field(min_length=1, max_length=50)
    bank_name: str | None = Field(default=None, max_length=120)
    account_type: str | None = Field(default=None, max_length=80)
    account_last_four: str | None = Field(default=None, max_length=4)

    @field_validator("account_last_four")
    @classmethod
    def validate_last_four(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        if len(value) != 4 or not value.isdigit():
            raise ValueError("account_last_four must contain exactly four digits")
        return value


class BeneficiaryCreate(BeneficiaryBase):
    pass


class BeneficiaryUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    relationship: str | None = Field(default=None, min_length=1, max_length=100)
    relationship_id: int | None = None
    relationship_other: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    city: str | None = Field(default=None, max_length=120)
    department: str | None = Field(default=None, max_length=100)
    municipality: str | None = Field(default=None, max_length=100)
    delivery_method: str | None = Field(default=None, min_length=1, max_length=50)
    bank_name: str | None = Field(default=None, max_length=120)
    account_type: str | None = Field(default=None, max_length=80)
    account_last_four: str | None = Field(default=None, max_length=4)
    is_active: bool | None = None

    @field_validator("account_last_four")
    @classmethod
    def validate_last_four(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        if len(value) != 4 or not value.isdigit():
            raise ValueError("account_last_four must contain exactly four digits")
        return value


class BeneficiaryRead(BeneficiaryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_id: int
    beneficiary_user_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
