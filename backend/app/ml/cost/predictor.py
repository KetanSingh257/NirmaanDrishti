"""
Cost predictor.

HOW TO INTEGRATE YOUR TRAINED MODEL
-----------------------------------
1. Drop artifacts into  backend/app/ml/cost/artifacts/
       model.pkl
       preprocessor.pkl
       feature_config.json

2. This class will automatically detect them via CostModelLoader.

3. The only method you may need to edit is `_predict_with_model`
   if your model output shape differs from a single float
   (predicted total expenditure in crore).

4. `_to_feature_frame` builds the feature matrix. Adjust column
   order there if your training pipeline used a different schema.

5. Do NOT change the public `predict()` return dict — the API
   contract and frontend depend on those keys.
"""

from __future__ import annotations

import logging
from typing import Any

from app.ml.cost.model_loader import loader
from app.schemas.prediction import CostPredictRequest

logger = logging.getLogger(__name__)


class CostPredictor:
    """Thin adapter: real model if present, else None (caller uses mock)."""

    def available(self) -> bool:
        return loader.is_ready

    def predict(self, payload: CostPredictRequest) -> dict[str, Any] | None:
        if not loader.is_ready:
            return None
        try:
            predicted_expenditure = float(self._predict_with_model(payload))
            return {
                "predicted_expenditure_cr": predicted_expenditure,
                "model_name": (loader.feature_config or {}).get(
                    "model_name", type(loader.model).__name__
                ),
                "used_real_model": True,
            }
        except Exception:
            logger.exception("Real cost model inference failed")
            return None

    def predict_many(self, payloads: list[CostPredictRequest]) -> list[dict[str, Any]] | None:
        if not loader.is_ready:
            return None
        try:
            frame = self._to_feature_frame_many(payloads)
            values = loader.model.predict(frame)
            model_name = (loader.feature_config or {}).get("model_name", type(loader.model).__name__)
            return [
                {"predicted_expenditure_cr": float(value), "model_name": model_name, "used_real_model": True}
                for value in values
            ]
        except Exception:
            logger.exception("Batch cost model inference failed")
            return None

    def _predict_with_model(self, payload: CostPredictRequest) -> float:
        """
        INTEGRATION POINT — replace / extend this method if needed.

        Default behaviour:
            1. Build a 1-row feature frame from the request.
            2. Apply preprocessor.pkl if it exists.
            3. Call model.predict(X) and return the first value.
        """
        X = self._to_feature_frame(payload)
        if loader.preprocessor is not None and not hasattr(loader.model, "named_steps"):
            X = loader.preprocessor.transform(X)
        y = loader.model.predict(X)
        value = y[0] if hasattr(y, "__len__") else y
        return float(value)

    def _to_feature_frame(self, payload: CostPredictRequest):
        """
        Build a pandas / numpy row matching the training feature order.

        Default numeric feature order (override via feature_config.json):
            original_cost_cr, revised_cost_cr, physical_progress_pct,
            previous_progress, previous_expenditure, project_age_days,
            days_to_original_completion, days_overdue
        """
        data = payload.model_dump()
        config = loader.feature_config or {}
        numeric = config.get(
            "features",
            [
                "original_cost_cr",
                "revised_cost_cr",
                "physical_progress_pct",
                "previous_progress",
                "previous_expenditure",
                "project_age_days",
                "days_to_original_completion",
                "days_overdue",
            ],
        )
        categorical = config.get("categorical", [])
        columns = list(numeric) + list(categorical)
        row = {col: data.get(col, 0) for col in columns}
        try:
            import pandas as pd

            return pd.DataFrame([row], columns=columns)
        except ImportError:
            import numpy as np

            return np.array([[row[c] for c in numeric]], dtype=float)

    def _to_feature_frame_many(self, payloads: list[CostPredictRequest]):
        config = loader.feature_config or {}
        numeric = config.get("features", [])
        categorical = config.get("categorical", [])
        columns = list(numeric) + list(categorical)
        rows = [{column: payload.model_dump().get(column, 0) for column in columns} for payload in payloads]
        try:
            import pandas as pd
            return pd.DataFrame(rows, columns=columns)
        except ImportError:
            import numpy as np
            return np.array([[row[column] for column in columns] for row in rows], dtype=float)
