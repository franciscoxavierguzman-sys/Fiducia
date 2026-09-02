from datetime import UTC, datetime
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.country import Country
from app.models.user import User
from app.repositories.users import create_user, get_user_by_email
from app.schemas.auth import LoginRequest, PasswordChangeRequest, PasswordResetRequest, PasswordResetResponse, TokenResponse
from app.core.rate_limit import client_rate_key, rate_limiter
from app.schemas.user import UserCreate, UserRead
from app.security.passwords import hash_password, verify_password
from app.security.tokens import create_access_token
from app.services.audit import log_audit_event
from app.services.email import send_password_reset_email

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    role = "CLIENT" if payload.role == "sender" else payload.role
    if role not in {"CLIENT", "RISK_ANALYST", "ADMIN"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_ROLE", "message": "Rol no permitido"},
        )
    country = db.scalar(select(Country).where(Country.name == payload.country, Country.is_destination_enabled.is_(True)))
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_COUNTRY", "message": "Pais no permitido"},
        )

    existing_user = get_user_by_email(db, payload.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "EMAIL_ALREADY_REGISTERED", "message": "El correo ya esta registrado"},
        )

    try:
        user = create_user(db, payload)
        log_audit_event(
            db,
            user_id=user.id,
            action="USER_REGISTERED",
            entity="user",
            entity_id=str(user.id),
            metadata={"country": user.country},
        )
        db.commit()
        db.refresh(user)
        return user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ROLE_NOT_FOUND", "message": "El rol solicitado no existe"},
        ) from None


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    rate_limiter.check(client_rate_key(request, f"login:{payload.email.lower()}"), limit=12, window_seconds=60)
    user = get_user_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Correo o contrasena incorrectos"},
        )

    log_audit_event(
        db,
        user_id=user.id,
        action="LOGIN",
        entity="user",
        entity_id=str(user.id),
        metadata=None,
    )
    db.commit()
    return TokenResponse(access_token=create_access_token(str(user.id)), must_change_password=user.must_change_password)


@router.post("/password/forgot", response_model=PasswordResetResponse)
def forgot_password(payload: PasswordResetRequest, request: Request, db: Session = Depends(get_db)) -> PasswordResetResponse:
    normalized_email = payload.email.lower()
    rate_limiter.check(client_rate_key(request, f"password-reset:{normalized_email}"), limit=5, window_seconds=300)
    user = get_user_by_email(db, normalized_email)
    generic_message = "Si el correo esta registrado, enviaremos una contrasena temporal."
    if user is None:
        log_audit_event(
            db,
            user_id=None,
            action="PASSWORD_RESET_REQUESTED_UNKNOWN_EMAIL",
            entity="user",
            entity_id=normalized_email,
            metadata=None,
        )
        db.commit()
        return PasswordResetResponse(message=generic_message)

    temporary_password = generate_temporary_password()
    user.password_hash = hash_password(temporary_password)
    user.must_change_password = True
    user.updated_at = datetime.now(UTC)
    delivery = send_password_reset_email(recipient=user.email, temporary_password=temporary_password)
    log_audit_event(
        db,
        user_id=user.id,
        action="PASSWORD_RESET_REQUESTED",
        entity="user",
        entity_id=str(user.id),
        metadata={"delivery": delivery["delivery"]},
    )
    db.commit()
    return PasswordResetResponse(
        message=generic_message,
        delivery=delivery["delivery"],
        temporary_password=temporary_password,
    )


@router.post("/password/change", response_model=UserRead)
def change_password(payload: PasswordChangeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserRead:
    current_user.password_hash = hash_password(payload.new_password)
    current_user.must_change_password = False
    current_user.updated_at = datetime.now(UTC)
    log_audit_event(
        db,
        user_id=current_user.id,
        action="PASSWORD_CHANGED",
        entity="user",
        entity_id=str(current_user.id),
        metadata={"forced_change": True},
    )
    db.commit()
    db.refresh(current_user)
    return current_user


def generate_temporary_password() -> str:
    alphabet = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(12))
        if any(character.isalpha() for character in password) and any(character.isdigit() for character in password):
            return password
