from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.funding_source import FundingSource
from app.schemas.funding_source import FundingSourceCreate, FundingSourceUpdate


def list_funding_sources(db: Session, user_id: int) -> list[FundingSource]:
    return list(
        db.scalars(
            select(FundingSource)
            .where(FundingSource.user_id == user_id)
            .order_by(FundingSource.is_default.desc(), FundingSource.created_at.desc())
        )
    )


def get_funding_source(db: Session, funding_source_id: int, user_id: int) -> FundingSource | None:
    source = db.get(FundingSource, funding_source_id)
    if source is None or source.user_id != user_id:
        return None
    return source


def create_funding_source(db: Session, user_id: int, payload: FundingSourceCreate) -> FundingSource:
    if payload.is_default:
        db.execute(update(FundingSource).where(FundingSource.user_id == user_id).values(is_default=False))
    elif not list_funding_sources(db, user_id):
        payload.is_default = True
    data = payload.model_dump(exclude={"account_number", "card_number", "card_cvv"})
    source = FundingSource(user_id=user_id, **data)
    db.add(source)
    db.flush()
    return source


def update_funding_source(db: Session, source: FundingSource, payload: FundingSourceUpdate) -> FundingSource:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(source, field, value)
    db.flush()
    return source


def set_default_funding_source(db: Session, source: FundingSource) -> FundingSource:
    db.execute(update(FundingSource).where(FundingSource.user_id == source.user_id).values(is_default=False))
    source.is_default = True
    source.is_active = True
    db.flush()
    return source
