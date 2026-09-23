from datetime import UTC, datetime
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserPasswordResetResponse, UserRead, UserUpdate
from app.security.passwords import hash_password
from app.services.audit import log_audit_event
from app.services.email import send_password_reset_email

router = APIRouter()
SUPPORT_ACCESS_ROLES = {"ADMIN", "SUPPORT"}


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user


@router.patch("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "email" and value is not None:
            normalized_email = value.lower()
            existing = db.scalar(select(User).where(User.email == normalized_email, User.id != current_user.id))
            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"code": "EMAIL_ALREADY_REGISTERED", "message": "El correo ya esta registrado"},
                )
            value = normalized_email
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


def require_support_access(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name not in SUPPORT_ACCESS_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "SUPPORT_ACCESS_REQUIRED", "message": "Acceso reservado para soporte"},
        )
    return current_user


@router.get("", response_model=list[UserRead])
def list_users(
    _: User = Depends(require_support_access),
    db: Session = Depends(get_db),
) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc(), User.id.desc())))


@router.post("/{user_id}/password-reset", response_model=UserPasswordResetResponse)
def reset_user_password(
    user_id: int,
    current_user: User = Depends(require_support_access),
    db: Session = Depends(get_db),
) -> UserPasswordResetResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "Usuario no encontrado"},
        )

    temporary_password = generate_temporary_password()
    user.password_hash = hash_password(temporary_password)
    user.must_change_password = True
    user.updated_at = datetime.now(UTC)
    delivery = send_password_reset_email(recipient=user.email, temporary_password=temporary_password)
    log_audit_event(
        db,
        user_id=current_user.id,
        action="SUPPORT_PASSWORD_RESET",
        entity="user",
        entity_id=str(user.id),
        metadata={"target_email": user.email, "delivery": delivery["delivery"]},
    )
    db.commit()
    db.refresh(user)
    return UserPasswordResetResponse(
        message="Contrasena temporal generada. El usuario debera cambiarla al iniciar sesion.",
        temporary_password=temporary_password,
        delivery=delivery["delivery"],
        user=user,
    )


@router.post("/{user_id}/unlock", response_model=UserRead)
def unlock_user(
    user_id: int,
    current_user: User = Depends(require_support_access),
    db: Session = Depends(get_db),
) -> User:
    user = get_support_target_user(db, user_id)
    user.is_active = True
    user.updated_at = datetime.now(UTC)
    log_audit_event(
        db,
        user_id=current_user.id,
        action="SUPPORT_USER_UNLOCKED",
        entity="user",
        entity_id=str(user.id),
        metadata={"target_email": user.email},
    )
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/lock", response_model=UserRead)
def lock_user(
    user_id: int,
    current_user: User = Depends(require_support_access),
    db: Session = Depends(get_db),
) -> User:
    user = get_support_target_user(db, user_id)
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CANNOT_LOCK_SELF", "message": "No puedes bloquear tu propio usuario"},
        )
    user.is_active = False
    user.updated_at = datetime.now(UTC)
    log_audit_event(
        db,
        user_id=current_user.id,
        action="SUPPORT_USER_LOCKED",
        entity="user",
        entity_id=str(user.id),
        metadata={"target_email": user.email},
    )
    db.commit()
    db.refresh(user)
    return user


def get_support_target_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "Usuario no encontrado"},
        )
    return user


def generate_temporary_password() -> str:
    alphabet = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(12))
        if any(character.isalpha() for character in password) and any(character.isdigit() for character in password):
            return password
