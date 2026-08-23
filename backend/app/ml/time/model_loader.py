"""Time model artifact loader — mirrors the cost loader."""

from __future__ import annotations

import logging
import json
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class TimeModelLoader:
    def __init__(self) -> None:
        settings = get_settings()
        self.model_path = Path(settings.time_model_path)
        self.preprocessor_path = Path(settings.time_preprocessor_path)
        self.feature_config_path = Path(settings.time_feature_config_path)
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
            logger.info("Time model not found at %s — using mock predictor.", self.model_path)
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
            logger.info("Loaded time model from %s", self.model_path)
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to load time model: %s", exc)
            self._model = None


loader = TimeModelLoader()
