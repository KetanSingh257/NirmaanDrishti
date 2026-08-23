"""
Cost model artifact loader.

INTEGRATION POINT
-----------------
Place the following files in  backend/app/ml/cost/artifacts/

    model.pkl              trained estimator (XGBoost / RF / LightGBM / sklearn)
    preprocessor.pkl       fitted ColumnTransformer / pipeline
    feature_config.json    ordered feature names + optional encodings

    {
      "features": [
        "original_cost_cr",
        "revised_cost_cr",
        "physical_progress_pct",
        "previous_progress",
        "previous_expenditure",
        "project_age_days",
        "days_to_original_completion",
        "days_overdue"
      ],
      "categorical": ["agency", "state"]
    }

This module never raises if files are missing — it simply reports
`is_ready = False` so the service layer can fall back to the mock engine.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class CostModelLoader:
    def __init__(self) -> None:
        settings = get_settings()
        self.model_path = Path(settings.cost_model_path)
        self.preprocessor_path = Path(settings.cost_preprocessor_path)
        self.feature_config_path = Path(settings.cost_feature_config_path)
        self._model = None
        self._preprocessor = None
        self._feature_config: dict | None = None
        self._tried = False

    @property
    def is_ready(self) -> bool:
        self._ensure_loaded()
        return self._model is not None

    @property
    def model(self):
        self._ensure_loaded()
        return self._model

    @property
    def preprocessor(self):
        self._ensure_loaded()
        return self._preprocessor

    @property
    def feature_config(self) -> dict | None:
        self._ensure_loaded()
        return self._feature_config

    def _ensure_loaded(self) -> None:
        if self._tried:
            return
        self._tried = True
        if not self.model_path.exists():
            logger.info("Cost model not found at %s — using mock predictor.", self.model_path)
            return
        try:
            import joblib

            self._model = joblib.load(self.model_path)
            if self.preprocessor_path.exists():
                self._preprocessor = joblib.load(self.preprocessor_path)
            if self.feature_config_path.exists():
                self._feature_config = json.loads(
                    self.feature_config_path.read_text(encoding="utf-8")
                )
            logger.info("Loaded cost model from %s", self.model_path)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to load cost model: %s", exc)
            self._model = None


loader = CostModelLoader()
