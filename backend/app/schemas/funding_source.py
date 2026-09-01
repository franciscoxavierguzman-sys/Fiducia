from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class FundingSourceCreate(BaseModel):
    type: str = Field(min_length=1, max_length=40)
    display_name: str = Field(min_length=1, max_length=120)
    provider: str | None = Field(default=None, max_length=120)
    last_four: str = Field(min_length=4, max_length=4)
    account_type: str | None = Field(default=None, max_length=40)
    account_number: str | None = Field(default=None, max_length=40)
    card_number: str | None = Field(default=None, max_length=19)
    card_expiry: str | None = Field(default=None, max_length=5)
    card_cvv: str | None = Field(default=None, max_length=4)
    currency: str = Field(min_length=3, max_length=3)
    is_default: bool = False

    @field_validator("last_four")
    @classmethod
    def validate_last_four(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("last_four must contain exactly four digits")
        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        allowed = {"CARD", "BANK_ACCOUNT", "DIGITAL_WALLET"}
        normalized = value.upper()
        if normalized not in allowed:
            raise ValueError("funding source type is not supported")
        return normalized

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in {"USD", "GTQ"}:
            raise ValueError("currency must be USD or GTQ")
        return normalized

    @field_validator("account_type")
    @classmethod
    def normalize_account_type(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        normalized = value.strip().upper()
        if normalized not in {"AHORRO", "MONETARIO"}:
            raise ValueError("account type must be AHORRO or MONETARIO")
        return "Ahorro" if normalized == "AHORRO" else "Monetario"

    @field_validator("account_number")
    @classmethod
    def validate_account_number(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        if not value.isdigit() or len(value) < 6:
            raise ValueError("account number must contain at least six digits")
        return value

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        if not value.isdigit() or len(value) < 13 or len(value) > 19:
            raise ValueError("card number must contain 13 to 19 digits")
        return value

    @field_validator("card_expiry")
    @classmethod
    def validate_card_expiry(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        if len(value) != 5 or value[2] != "/" or not value[:2].isdigit() or not value[3:].isdigit():
            raise ValueError("card expiry must use MM/YY format")
        month = int(value[:2])
        if month < 1 or month > 12:
            raise ValueError("card expiry month is not valid")
        return value

    @field_validator("card_cvv")
    @classmethod
    def validate_card_cvv(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        if not value.isdigit() or len(value) not in {3, 4}:
            raise ValueError("card cvv must contain three or four digits")
        return value

    @model_validator(mode="after")
    def validate_sensitive_inputs(self) -> "FundingSourceCreate":
        if self.type == "BANK_ACCOUNT":
            if not self.account_type:
                raise ValueError("account type is required for bank accounts")
            if not self.account_number:
                raise ValueError("account number is required for bank accounts")
            if self.last_four != self.account_number[-4:]:
                raise ValueError("last four must match account number")
            self.card_expiry = None
        if self.type == "CARD":
            if not self.card_number:
                raise ValueError("card number is required")
            if self.last_four != self.card_number[-4:]:
                raise ValueError("last four must match card number")
            if not self.card_expiry:
                raise ValueError("card expiry is required")
            if not self.card_cvv:
                raise ValueError("card cvv is required")
            self.account_type = None
        if self.type == "DIGITAL_WALLET":
            self.account_type = None
            self.card_expiry = None
        return self


class FundingSourceUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    provider: str | None = Field(default=None, max_length=120)
    account_type: str | None = Field(default=None, max_length=40)
    card_expiry: str | None = Field(default=None, max_length=5)
    is_active: bool | None = None


class FundingSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: str
    display_name: str
    provider: str | None
    last_four: str
    account_type: str | None
    card_expiry: str | None
    currency: str
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
