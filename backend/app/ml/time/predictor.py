"""Time predictor adapter. Same integration pattern as the cost model."""

from __future__ import annotations

import logging
from typing import Any

from app.ml.time.model_loader import loader
from app.schemas.prediction import TimePredictRequest

logger = logging.getLogger(__name__)


class TimePredictor:
    def available(self) -> bool:
        return loader.is_ready

    def predict(self, payload: TimePredictRequest) -> dict[str, Any] | None:
        if not loader.is_ready:
            return None
        try:
            predicted_delay = float(self._predict_with_model(payload))
            return {
                "predicted_delay_days": int(round(predicted_delay)),
                "model_name": type(loader.model).__name__,
                "used_real_model": True,
            }
        except Exception as exc:
            logger.warning("Real time model inference failed, falling back: %s", exc)
            return None

    def _predict_with_model(self, payload: TimePredictRequest) -> float:
        data = payload.model_dump()
        features = [
            "physical_progress_pct",
            "previous_progress",
            "project_age_days",
            "days_to_original_completion",
            "days_overdue",
            "original_cost_cr",
            "revised_cost_cr",
        ]
        try:
            import pandas as pd

            X = pd.DataFrame([{k: data.get(k, 0) for k in features}])
        except ImportError:
            import numpy as np

            X = np.array([[data.get(k, 0) for k in features]], dtype=float)
        if loader.preprocessor is not None:
            X = loader.preprocessor.transform(X)
        y = loader.model.predict(X)
        value = y[0] if hasattr(y, "__len__") else y
        return float(value)
