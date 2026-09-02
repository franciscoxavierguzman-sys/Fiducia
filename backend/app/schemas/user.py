from datetime import date, datetime
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=6, max_length=30)
    country: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str | None = Field(default=None, min_length=8, max_length=128)
    terms_accepted: bool = False
    human_check_accepted: bool = False
    document_type: str = Field(default="DPI", min_length=3, max_length=30)
    fictitious_document_id: str | None = Field(default=None, max_length=100)
    birth_date: date | None = None
    occupation: str | None = Field(default=None, max_length=150)
    role: str = "CLIENT"

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        cleaned = value.replace(" ", "").replace("-", "")
        if not cleaned.isdigit() or len(cleaned) < 6:
            raise ValueError("phone must contain at least six digits")
        return value

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(character.isalpha() for character in value) or not any(character.isdigit() for character in value):
            raise ValueError("password must contain letters and numbers")
        return value

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in {"DPI", "PASSPORT", "PASAPORTE"}:
            raise ValueError("document type is not supported")
        return "PASSPORT" if normalized == "PASAPORTE" else normalized

    @model_validator(mode="after")
    def validate_registration(self) -> "UserCreate":
        if self.confirm_password is not None and self.password != self.confirm_password:
            raise ValueError("passwords do not match")
        if not self.terms_accepted:
            raise ValueError("terms must be accepted")
        if not self.human_check_accepted:
            raise ValueError("human check must be accepted")
        if self.birth_date is None:
            raise ValueError("birth date is required")
        if self.birth_date >= date.today():
            raise ValueError("birth date must be in the past")
        if not self.fictitious_document_id:
            raise ValueError("document number is required")
        document_number = self.fictitious_document_id.strip()
        if self.document_type == "DPI":
            if not document_number.isdigit() or len(document_number) != 13:
                raise ValueError("DPI must contain exactly 13 digits")
        elif not re.fullmatch(r"[A-Za-z0-9-]{6,20}", document_number):
            raise ValueError("passport must contain 6 to 20 letters, numbers or hyphens")
        return self


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=6, max_length=30)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    document_type: str | None = Field(default=None, min_length=3, max_length=30)
    fictitious_document_id: str | None = Field(default=None, max_length=100)
    birth_date: date | None = None
    occupation: str | None = Field(default=None, max_length=150)


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    country: str
    document_type: str | None
    fictitious_document_id: str | None
    birth_date: date | None
    occupation: str | None
    is_active: bool
    must_change_password: bool
    created_at: datetime
    role: RoleRead
