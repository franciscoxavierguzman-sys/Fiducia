from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.sqlite_migrations import ensure_sqlite_schema_compatibility
from app.db.session import Base, engine
from app.models import (
    audit_log,
    beneficiary,
    beneficiary_relationship,
    country,
    department,
    exchange_rate,
    forecast,
    funding_source,
    municipality,
    remittance_corridor,
    risk_assessment,
    remittance_status_history,
    role,
    transaction,
    user,
)
from app.services.seed import seed_default_roles


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_schema_compatibility()
    seed_default_roles()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="FIDUCIA remittance platform API.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
