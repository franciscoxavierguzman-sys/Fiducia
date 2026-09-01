from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "FIDUCIA"
    app_version: str = "1.0.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'database' / 'fiducia.db').as_posix()}"
    secret_key: str = "change-this-development-secret"
    access_token_expire_minutes: int = 60
    backend_cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"
    )
    commission_rate: float = Field(default=0.0225, ge=0)
    default_exchange_rate_usd_gtq: float = Field(default=7.80, gt=0)
    minimum_remittance_amount: float = Field(default=10, gt=0)
    maximum_remittance_amount: float = Field(default=5000, gt=0)
    risk_weight_rules: float = Field(default=0.40, ge=0)
    risk_weight_ml: float = Field(default=0.60, ge=0)
    risk_weight_anomaly: float = Field(default=0.00, ge=0)
    default_model_version: str = "not_trained"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str | AnyHttpUrl]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
