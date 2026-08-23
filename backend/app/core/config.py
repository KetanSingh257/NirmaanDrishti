"""Application configuration.

Risk weights and thresholds live here so the intelligence layer can be
tuned without touching service logic.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]
ML_DIR = Path(__file__).resolve().parents[1] / "ml"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "NIRMAANDRISHTI AI"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # SQLite by default. Set DATABASE_URL=postgresql+psycopg2://user:pass@host/db
    # to switch to PostgreSQL without any other code changes.
    database_url: str = f"sqlite:///{ROOT_DIR / 'nirmaandrishti.db'}"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Intelligence layer weights (must sum to 1.0)
    cost_risk_weight: float = 0.40
    time_risk_weight: float = 0.35
    trend_risk_weight: float = 0.25

    # Overall health thresholds
    healthy_max: int = 30
    watch_max: int = 50
    at_risk_max: int = 70

    # ML artifact locations — drop trained files here later
    cost_model_path: str = str(ML_DIR / "cost" / "artifacts" / "model.pkl")
    cost_preprocessor_path: str = str(ML_DIR / "cost" / "artifacts" / "preprocessor.pkl")
    cost_feature_config_path: str = str(ML_DIR / "cost" / "artifacts" / "feature_config.json")
    time_model_path: str = str(ML_DIR / "time" / "artifacts" / "model.pkl")
    time_preprocessor_path: str = str(ML_DIR / "time" / "artifacts" / "preprocessor.pkl")
    time_feature_config_path: str = str(ML_DIR / "time" / "artifacts" / "feature_config.json")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
