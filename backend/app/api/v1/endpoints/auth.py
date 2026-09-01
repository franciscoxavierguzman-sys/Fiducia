from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.country import Country
from app.repositories.users import create_user, get_user_by_email
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.rate_limit import client_rate_key, rate_limiter
from app.schemas.user import UserCreate, UserRead
from app.security.passwords import verify_password
from app.security.tokens import create_access_token
from app.services.audit import log_audit_event

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
    return TokenResponse(access_token=create_access_token(str(user.id)))
