from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.remittance import RemittanceCorridorRead, RemittanceSimulationRequest, RemittanceSimulationResponse
from app.services.remittances import list_active_corridors, simulate_remittance

router = APIRouter()


@router.get("/corridors", response_model=list[RemittanceCorridorRead])
def corridors(db: Session = Depends(get_db)):
    return list_active_corridors(db)


@router.post("/simulate", response_model=RemittanceSimulationResponse)
def simulate(
    payload: RemittanceSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return simulate_remittance(db, payload, current_user.id)
