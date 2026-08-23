"""Time Intelligence Engine — delay and completion risk."""

from __future__ import annotations

from datetime import date, timedelta

from app.ml.time.predictor import TimePredictor
from app.schemas.prediction import TimePredictRequest, TimePredictResponse


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


class TimePredictionService:
    def __init__(self) -> None:
        self._ml = TimePredictor()

    def predict(self, data: TimePredictRequest) -> TimePredictResponse:
        ml_out = self._ml.predict(data)
        mock_delay, remaining_days = self._mock_delay(data)
        delay = ml_out["predicted_delay_days"] if ml_out else mock_delay
        model_name = (
            ml_out["model_name"] if ml_out else "Gradient Boosted Time Model"
        )
        used_real = bool(ml_out)

        remaining_days = max(int(remaining_days), 0)
        est = date.today() + timedelta(days=remaining_days)
        delay = max(int(delay), 0)

        progress = data.physical_progress_pct
        overdue_boost = 8 if data.days_overdue > 180 and progress < 70 else 0
        slip_boost = 8 if progress < 30 and data.days_to_original_completion < 0 else 0
        delay_probability = _clamp(10 + delay / 12 + overdue_boost + slip_boost, 5, 90)

        # Score from forecast residual delay, not from historical overdue alone.
        # Near-complete work is capped so a late-but-finishing job is not "critical".
        if progress >= 88:
            risk, score = ("MEDIUM", _clamp(24 + delay / 10, 18, 42)) if delay > 40 else ("LOW", _clamp(8 + delay / 8, 6, 24))
        elif delay >= 360 or (progress < 45 and data.days_overdue > 300):
            risk, score = "CRITICAL", _clamp(66 + delay / 50, 66, 88)
        elif delay >= 160:
            risk, score = "HIGH", _clamp(48 + delay / 28, 48, 65)
        elif delay >= 55:
            risk, score = "MEDIUM", _clamp(26 + delay / 14, 26, 47)
        else:
            risk, score = "LOW", _clamp(6 + delay / 7, 5, 25)

        confidence = _clamp(60 + data.physical_progress_pct * 0.2 + (6 if data.previous_progress else 0), 55, 93)

        return TimePredictResponse(
            predicted_delay_days=delay,
            estimated_completion_date=est,
            delay_probability=round(delay_probability, 0),
            remaining_days=remaining_days,
            risk_level=risk,
            risk_score=round(score, 1),
            confidence_score=round(confidence, 0),
            model_name=model_name,
            explanations=self._explain(data, delay, remaining_days),
            used_real_model=used_real,
        )

    def _mock_delay(self, data: TimePredictRequest) -> tuple[int, int]:
        """
        Heuristic stand-in for a delay regressor.

        REPLACE by placing model.pkl in app/ml/time/artifacts/.
        """
        progress = _clamp(data.physical_progress_pct, 0.4, 99.9)
        prev = _clamp(data.previous_progress, 0.0, progress)
        age = max(data.project_age_days, 30)
        remaining_pct = 100.0 - progress

        lifetime_rate = progress / age  # % per day
        recent_rate = max(progress - prev, 0.05) / 30.0
        blended = 0.45 * lifetime_rate + 0.55 * recent_rate
        blended = max(blended, 0.004)

        raw_remaining = remaining_pct / blended
        # Cost revision often correlates with schedule slip
        if data.revised_cost_cr > data.original_cost_cr * 1.1:
            raw_remaining *= 1.12
        if data.days_overdue > 0:
            raw_remaining *= 1.0 + min(data.days_overdue / 800.0, 0.35)

        remaining_days = int(round(_clamp(raw_remaining, 10, 2200)))
        planned_left = max(data.days_to_original_completion, 0)
        delay = remaining_days - planned_left
        if data.days_overdue > 0:
            delay = max(delay, data.days_overdue + int(remaining_pct / max(blended, 0.01) * 0.15))
        if progress >= 99:
            delay = min(delay, data.days_overdue)
            remaining_days = min(remaining_days, 20)
        return max(delay, 0), remaining_days

    def _explain(self, data: TimePredictRequest, delay: int, remaining: int) -> list[str]:
        notes: list[str] = []
        if data.days_overdue > 0:
            notes.append(
                f"Already {data.days_overdue} days past the original completion date."
            )
        planned_span = data.project_age_days + max(data.days_to_original_completion, 0)
        expected_progress = (
            (data.project_age_days / planned_span) * 100 if planned_span else data.physical_progress_pct
        )
        if data.physical_progress_pct + 8 < expected_progress:
            gap = expected_progress - data.physical_progress_pct
            notes.append(
                f"Physical progress trails the linear schedule by ~{gap:.0f} percentage points."
            )
        if data.previous_progress and data.physical_progress_pct - data.previous_progress < 1.2:
            notes.append("Latest reporting window shows near-stalled physical progress.")
        if delay > 180:
            notes.append(
                f"At the current velocity the project needs ~{remaining} more days to finish."
            )
        if data.revised_cost_cr > data.original_cost_cr * 1.15:
            notes.append("A large cost revision usually accompanies further schedule slippage.")
        if delay < 30 and data.days_overdue == 0:
            notes.append("Schedule performance is close to the sanctioned timeline.")
        if not notes:
            notes.append(f"Predicted delay of {delay} days based on current progress velocity.")
        return notes[:5]
