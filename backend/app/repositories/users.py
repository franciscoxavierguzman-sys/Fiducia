from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate
from app.security.passwords import hash_password


def get_role_by_name(db: Session, name: str) -> Role | None:
    return db.scalar(select(Role).where(Role.name == name))


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create_user(db: Session, payload: UserCreate) -> User:
    role_name = "CLIENT" if payload.role == "sender" else payload.role
    role = get_role_by_name(db, role_name)
    if role is None:
        raise ValueError("ROLE_NOT_FOUND")

    user = User(
        role_id=role.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email.lower(),
        phone=payload.phone,
        country=payload.country,
        password_hash=hash_password(payload.password),
        document_type=payload.document_type,
        fictitious_document_id=payload.fictitious_document_id,
        birth_date=payload.birth_date,
        occupation=payload.occupation,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
