from typing import Any

from pydantic import BaseModel, Field


class MLPredictRequest(BaseModel):
    features: dict[str, Any] = Field(default_factory=dict)


class MLFeatureContribution(BaseModel):
    feature: str
    importance: float
    method: str | None = None


class MLPredictResponse(BaseModel):
    ml_probability: float
    model_version: str
    threshold: float
    classification: str
    classification_label: str
    top_features: list[MLFeatureContribution] = Field(default_factory=list)


class MLModelInfo(BaseModel):
    available: bool
    model_name: str | None = None
    model_version: str | None = None
    algorithm: str | None = None
    selected_model: str | None = None
    trained_at: str | None = None
    threshold: float | None = None
    features: list[str] = Field(default_factory=list)
    dataset_hash: str | None = None
    message: str | None = None

