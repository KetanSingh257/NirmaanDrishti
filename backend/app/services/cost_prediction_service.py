"""Cost Intelligence Engine.

Public contract is stable. Swap the mock body by dropping a trained
model into app/ml/cost/artifacts/ — this service will pick it up.
"""

from __future__ import annotations

from app.ml.cost.predictor import CostPredictor
from app.schemas.prediction import CostPredictRequest, CostPredictResponse


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


class CostPredictionService:
    def __init__(self) -> None:
        self._ml = CostPredictor()

    def predict(self, data: CostPredictRequest) -> CostPredictResponse:
        ml_out = self._ml.predict(data)
        if ml_out is not None:
            return self._finalize(data, ml_out["predicted_expenditure_cr"], ml_out)

        predicted = self._mock_predict(data)
        return self._finalize(data, predicted, {"model_name": "XGBoost Cost Regressor", "used_real_model": False})

    def _mock_predict(self, data: CostPredictRequest) -> float:
        """
        Deterministic heuristic that mimics a cost-overrun regressor.

        REPLACE THIS by placing model.pkl in app/ml/cost/artifacts/.
        Do not change `_finalize` or the response schema.
        """
        original = max(data.original_cost_cr, 0.01)
        revised = max(data.revised_cost_cr, original)
        current = max(data.current_expenditure_cr, 0.0)
        progress = _clamp(data.physical_progress_pct, 0.4, 100.0)
        prev_progress = _clamp(data.previous_progress, 0.0, progress)
        overdue = max(data.days_overdue, 0)

        # Price remaining work off the sanctioned leftover, not the early-stage unit cost.
        sanctioned_left = max(revised - current, revised * (100 - progress) / 100.0 * 0.25)
        spend_frac = current / revised
        prog_frac = progress / 100.0
        pace = spend_frac / max(prog_frac, 0.02)  # >1 = spending faster than physical progress

        recent_delta = progress - prev_progress
        stall = 1.0
        if recent_delta < 0.6 and progress < 85:
            stall = 1.08
        if recent_delta < 0.25 and progress < 70:
            stall = 1.18

        overdue_nudge = 1.0 + min(overdue / 1800.0, 0.12)
        pace_factor = _clamp(0.92 + max(pace - 1.0, 0) * 0.7, 0.92, 1.55)
        predicted_total = current + sanctioned_left * pace_factor * stall * overdue_nudge

        if progress >= 90:
            predicted_total = min(predicted_total, max(revised, current) * 1.05)
        if progress < 15:
            # Mobilisation spend is a poor unit-cost signal — stay close to revised.
            predicted_total = min(predicted_total, revised * 1.12)

        ceiling = max(revised * 1.55, current * 1.15)
        return round(_clamp(predicted_total, current, ceiling), 2)

    def _finalize(
        self, data: CostPredictRequest, predicted: float, meta: dict
    ) -> CostPredictResponse:
        original = max(data.original_cost_cr, 0.01)
        revised = max(data.revised_cost_cr, original)
        current = data.current_expenditure_cr
        predicted = max(predicted, current)
        overrun = max(0.0, predicted - original)
        overrun_pct = (overrun / original) * 100.0

        # Display overrun vs original (API contract). Score risk on incremental
        # slip versus the revised envelope so already-sanctioned revisions do
        # not automatically mark a well-tracked project as critical.
        incr_pct = max(0.0, (predicted - revised) / revised * 100.0)
        revision_pct = max(0.0, (revised - original) / original * 100.0)
        risk_input = incr_pct + revision_pct * 0.22
        if data.physical_progress_pct < 40 and revision_pct > 30:
            risk_input += 12
        if data.days_overdue > 200 and incr_pct > 5:
            risk_input += 8

        if risk_input >= 38:
            risk, score = "CRITICAL", _clamp(68 + risk_input * 0.35, 68, 90)
        elif risk_input >= 20:
            risk, score = "HIGH", _clamp(50 + risk_input * 0.4, 50, 67)
        elif risk_input >= 8:
            risk, score = "MEDIUM", _clamp(28 + risk_input * 0.8, 28, 49)
        else:
            risk, score = "LOW", _clamp(6 + risk_input * 1.4, 5, 27)

        progress = data.physical_progress_pct
        confidence = _clamp(62 + progress * 0.22 + (8 if data.previous_progress else 0), 58, 94)

        return CostPredictResponse(
            predicted_expenditure_cr=round(predicted, 2),
            current_expenditure_cr=round(current, 2),
            predicted_overrun_cr=round(overrun, 2),
            overrun_percentage=round(overrun_pct, 1),
            risk_level=risk,
            risk_score=round(score, 1),
            confidence_score=round(confidence, 0),
            model_name=meta.get("model_name", "XGBoost Cost Regressor"),
            explanations=self._explain(data, predicted, overrun_pct, risk),
            used_real_model=bool(meta.get("used_real_model", False)),
        )

    def _explain(
        self, data: CostPredictRequest, predicted: float, overrun_pct: float, risk: str
    ) -> list[str]:
        notes: list[str] = []
        if data.revised_cost_cr > data.original_cost_cr * 1.05:
            delta = data.revised_cost_cr - data.original_cost_cr
            pct = (delta / data.original_cost_cr) * 100
            notes.append(
                f"Sanctioned cost already revised upward by ₹{delta:,.0f} Cr ({pct:.1f}%)."
            )
        expected = data.original_cost_cr * (data.physical_progress_pct / 100.0)
        if expected and data.current_expenditure_cr > expected * 1.15:
            notes.append(
                "Expenditure is running ahead of physical progress — a classic overrun signal."
            )
        if data.days_overdue > 30:
            notes.append(
                f"Project is {data.days_overdue} days past the original completion date, "
                "which typically inflates remaining unit cost."
            )
        if data.physical_progress_pct < 40 and data.project_age_days > 700:
            notes.append("Low physical progress relative to project age indicates cost leakage.")
        if data.previous_progress and data.physical_progress_pct - data.previous_progress < 1.5:
            notes.append("Recent progress increment is weak; remaining work will cost more per percent.")
        if overrun_pct < 5:
            notes.append("Spend trajectory is broadly aligned with the sanctioned envelope.")
        if not notes:
            notes.append(f"Model assigns {risk} cost risk based on burn-rate and remaining scope.")
        return notes[:5]
