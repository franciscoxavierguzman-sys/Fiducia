from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ml_risk import MLModelInfo, MLPredictRequest, MLPredictResponse
from app.schemas.risk_engine import (
    RiskAssessmentRead,
    RiskAssessmentWithRemittance,
    RiskDashboardMetrics,
    RiskEngineInfo,
    RiskReviewRequest,
)
from app.services.ml_risk import get_model_info, get_model_metrics, predict_fraud_probability
from app.services.risk_engine import (
    evaluate_remittance_by_id,
    get_assessment_or_404,
    get_latest_assessment_for_remittance,
    list_assessments,
    review_assessment,
    risk_dashboard_metrics,
    risk_engine_info,
)

router = APIRouter()


def require_risk_access(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name not in {"ADMIN", "RISK_ANALYST"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "RISK_FORBIDDEN", "message": "Inteligencia de riesgo disponible solo para perfiles autorizados"},
        )
    return current_user


@router.get("/ml/model-info", response_model=MLModelInfo)
def read_model_info(_: User = Depends(require_risk_access)) -> MLModelInfo:
    return get_model_info()


@router.get("/ml/metrics")
def read_model_metrics(_: User = Depends(require_risk_access)) -> dict:
    return get_model_metrics()


@router.post("/ml/predict", response_model=MLPredictResponse)
def predict_ml_risk(payload: MLPredictRequest, _: User = Depends(require_risk_access)) -> MLPredictResponse:
    return predict_fraud_probability(payload.features)


@router.get("/engine-info", response_model=RiskEngineInfo)
def read_risk_engine_info(_: User = Depends(require_risk_access)) -> dict:
    return risk_engine_info()


@router.get("/dashboard", response_model=RiskDashboardMetrics)
def read_risk_dashboard(_: User = Depends(require_risk_access), db: Session = Depends(get_db)) -> dict:
    return risk_dashboard_metrics(db)


@router.get("/assessments", response_model=list[RiskAssessmentWithRemittance])
def read_assessments(
    pending_only: bool = False,
    _: User = Depends(require_risk_access),
    db: Session = Depends(get_db),
) -> list[RiskAssessmentWithRemittance]:
    return list_assessments(db, only_pending=pending_only)


@router.get("/assessments/{assessment_id}", response_model=RiskAssessmentRead)
def read_assessment(assessment_id: int, _: User = Depends(require_risk_access), db: Session = Depends(get_db)):
    return get_assessment_or_404(db, assessment_id)


@router.get("/remittances/{remittance_id}", response_model=RiskAssessmentRead)
def read_remittance_assessment(remittance_id: int, _: User = Depends(require_risk_access), db: Session = Depends(get_db)):
    assessment = get_latest_assessment_for_remittance(db, remittance_id)
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RISK_ASSESSMENT_NOT_FOUND", "message": "La remesa aun no tiene evaluacion de riesgo"},
        )
    return assessment


@router.post("/remittances/{remittance_id}/evaluate", response_model=RiskAssessmentRead)
def evaluate_risk_for_remittance(
    remittance_id: int,
    current_user: User = Depends(require_risk_access),
    db: Session = Depends(get_db),
):
    return evaluate_remittance_by_id(db, remittance_id, current_user)


@router.post("/assessments/{assessment_id}/review", response_model=RiskAssessmentRead)
def review_risk_assessment(
    assessment_id: int,
    payload: RiskReviewRequest,
    current_user: User = Depends(require_risk_access),
    db: Session = Depends(get_db),
):
    return review_assessment(db, assessment_id, current_user, payload.decision, payload.reason)
