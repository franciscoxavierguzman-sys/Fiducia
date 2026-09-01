from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()


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
