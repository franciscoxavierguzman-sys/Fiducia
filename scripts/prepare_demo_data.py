from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

os.environ.setdefault("SECRET_KEY", "demo-data-local-secret")

from app.db.session import Base, SessionLocal, engine
from app.models.user import User
from app.repositories.users import get_user_by_email
from app.schemas.user import UserCreate
from app.services.seed import seed_default_roles
from app.repositories.users import create_user


DEMO_USERS = [
    ("demo.client@fiducia.local", "CLIENT"),
    ("demo.risk@fiducia.local", "RISK_ANALYST"),
    ("demo.admin@fiducia.local", "ADMIN"),
]


def ensure_demo_users() -> list[dict]:
    Base.metadata.create_all(bind=engine)
    seed_default_roles()
    created: list[dict] = []
    with SessionLocal() as db:
        for email, role in DEMO_USERS:
            existing = get_user_by_email(db, email)
            if existing is None:
                user = create_user(
                    db,
                    UserCreate(
                        first_name="Demo",
                        last_name=role.title().replace("_", ""),
                        email=email,
                        phone="55551234",
                        country="Guatemala",
                        password="Password123",
                        confirm_password="Password123",
                        terms_accepted=True,
                        human_check_accepted=True,
                        document_type="DPI",
                        fictitious_document_id="1234567890123",
                        birth_date="1995-05-15",
                        occupation="Demo",
                        role=role,
                    ),
                )
                created.append({"email": email, "role": role, "created": True, "id": user.id})
            else:
                created.append({"email": email, "role": existing.role.name, "created": False, "id": existing.id})
        db.commit()
    return created


def main() -> int:
    payload = {
        "users": ensure_demo_users(),
        "password": "Password123",
        "note": "Credenciales solo para demo local. No usar en produccion.",
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
