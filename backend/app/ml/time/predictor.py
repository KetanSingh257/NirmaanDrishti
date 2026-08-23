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
                "model_name": (loader.feature_config or {}).get(
                    "model_name", type(loader.model).__name__
                ),
                "used_real_model": True,
            }
        except Exception:
            logger.exception("Real time model inference failed")
            return None

    def predict_many(self, payloads: list[TimePredictRequest]) -> list[dict[str, Any]] | None:
        if not loader.is_ready:
            return None
        try:
            frame = self._to_feature_frame_many(payloads)
            values = loader.model.predict(frame)
            model_name = (loader.feature_config or {}).get("model_name", type(loader.model).__name__)
            return [
                {"predicted_delay_days": int(round(float(value))), "model_name": model_name, "used_real_model": True}
                for value in values
            ]
        except Exception:
            logger.exception("Batch time model inference failed")
            return None

    def _predict_with_model(self, payload: TimePredictRequest) -> float:
        data = payload.model_dump()
        config = loader.feature_config or {}
        features = list(config.get("features", [])) + list(config.get("categorical", []))
        if not features:
            features = [
                "project_age_days", "physical_progress_pct", "previous_progress",
                "progress_change", "original_cost_cr", "revised_cost_cr",
                "cumulative_expenditure_cr", "previous_expenditure", "expenditure_change",
                "cost_utilization_pct", "expenditure_progress_gap", "agency", "state",
            ]
        try:
            import pandas as pd

            X = pd.DataFrame([{k: data.get(k, 0) for k in features}])
        except ImportError:
            import numpy as np

            X = np.array([[data.get(k, 0) for k in features]], dtype=float)
        if loader.preprocessor is not None and not hasattr(loader.model, "named_steps"):
            X = loader.preprocessor.transform(X)
        y = loader.model.predict(X)
        value = y[0] if hasattr(y, "__len__") else y
        return float(value)

    def _to_feature_frame_many(self, payloads: list[TimePredictRequest]):
        config = loader.feature_config or {}
        features = list(config.get("features", [])) + list(config.get("categorical", []))
        rows = [{feature: payload.model_dump().get(feature, 0) for feature in features} for payload in payloads]
        try:
            import pandas as pd
            return pd.DataFrame(rows, columns=features)
        except ImportError:
            import numpy as np
            return np.array([[row[feature] for feature in features] for row in rows], dtype=float)
