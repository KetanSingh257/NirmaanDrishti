"""Trend Intelligence Engine.

This is a real analytical engine — not a random mock. It consumes the
project's historical updates and computes velocity, efficiency, and
direction of travel.
"""

from __future__ import annotations

from datetime import date

from app.schemas.prediction import HistoryPoint, TrendAnalyzeResponse


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


class TrendEngine:
    def analyze(self, history: list[HistoryPoint] | list[dict]) -> TrendAnalyzeResponse:
        points = self._normalize(history)
        if len(points) < 2:
            return TrendAnalyzeResponse(
                trend="INSUFFICIENT_DATA",
                trend_score=40,
                progress_velocity=0,
                expenditure_velocity=0,
                cost_efficiency=1.0,
                progress_slowdown=0,
                expenditure_acceleration=0,
                risk_level="MEDIUM",
                risk_score=40,
                insights=["Not enough historical updates to compute a reliable trend."],
                series=points,
            )

        points = sorted(points, key=lambda p: p.date)
        mid = max(len(points) // 2, 1)
        early, late = points[: mid + 1], points[mid:]
        if len(late) < 2:
            late = points[-2:]
            early = points[:2]

        early_prog_v = self._velocity(
            early[0].physical_progress_pct,
            early[-1].physical_progress_pct,
            early[0].date,
            early[-1].date,
        )
        late_prog_v = self._velocity(
            late[0].physical_progress_pct,
            late[-1].physical_progress_pct,
            late[0].date,
            late[-1].date,
        )
        early_exp_v = self._velocity(
            early[0].expenditure_cr, early[-1].expenditure_cr, early[0].date, early[-1].date
        )
        late_exp_v = self._velocity(
            late[0].expenditure_cr, late[-1].expenditure_cr, late[0].date, late[-1].date
        )

        # % change of recent velocity vs early velocity (monthly units)
        if abs(early_prog_v) > 1e-6:
            progress_velocity = ((late_prog_v - early_prog_v) / abs(early_prog_v)) * 100
        else:
            progress_velocity = 0.0 if late_prog_v <= 0 else 40.0

        if abs(early_exp_v) > 1e-6:
            expenditure_velocity = ((late_exp_v - early_exp_v) / abs(early_exp_v)) * 100
        else:
            expenditure_velocity = 0.0

        first, last = points[0], points[-1]
        progress_gain = max(last.physical_progress_pct - first.physical_progress_pct, 0.01)
        spend_gain = max(last.expenditure_cr - first.expenditure_cr, 0.01)
        # Higher is better: progress points earned per crore spent in the window
        raw_eff = progress_gain / spend_gain
        # Normalise around a typical 0.04–0.15 band into 0–1.5
        cost_efficiency = _clamp(raw_eff * 12.0, 0.15, 1.8)

        progress_slowdown = -progress_velocity if progress_velocity < 0 else 0.0
        expenditure_acceleration = expenditure_velocity if expenditure_velocity > 0 else 0.0

        # Composite trend score (higher = worse)
        score = 22.0
        score += _clamp(progress_slowdown * 0.42, 0, 28)
        if expenditure_velocity > 18 and progress_velocity < -8:
            score += 14
        elif expenditure_velocity > 20 and progress_velocity < 5:
            score += 8
        if cost_efficiency < 0.45:
            score += 12
        elif cost_efficiency < 0.7:
            score += 5
        if late_prog_v <= 0.04:
            score += 12  # stalled
        if progress_velocity > 10 and cost_efficiency >= 0.85:
            score -= 10
        score = _clamp(score, 6, 90)

        if score >= 70 or (progress_velocity < -20 and expenditure_velocity > 10):
            trend, risk = "DETERIORATING", "HIGH"
        elif score >= 52 or progress_velocity < -8:
            trend, risk = "WEAKENING", "MEDIUM"
        elif progress_velocity > 12 and cost_efficiency >= 0.85:
            trend, risk = "IMPROVING", "LOW"
        else:
            trend, risk = "STABLE", "LOW" if score < 40 else "MEDIUM"

        if trend == "DETERIORATING":
            risk_level = "CRITICAL" if score >= 80 else "HIGH"
        elif trend == "WEAKENING":
            risk_level = "MEDIUM"
        elif trend == "IMPROVING":
            risk_level = "LOW"
        else:
            risk_level = "LOW" if score < 40 else "MEDIUM"

        insights = self._insights(
            progress_velocity,
            expenditure_velocity,
            cost_efficiency,
            late_prog_v,
            trend,
        )

        return TrendAnalyzeResponse(
            trend=trend,
            trend_score=round(score, 1),
            progress_velocity=round(progress_velocity, 1),
            expenditure_velocity=round(expenditure_velocity, 1),
            cost_efficiency=round(cost_efficiency, 2),
            progress_slowdown=round(progress_slowdown, 1),
            expenditure_acceleration=round(expenditure_acceleration, 1),
            risk_level=risk_level,
            risk_score=round(score, 1),
            insights=insights,
            series=points,
        )

    def _normalize(self, history: list) -> list[HistoryPoint]:
        out: list[HistoryPoint] = []
        for item in history:
            if isinstance(item, HistoryPoint):
                out.append(item)
            elif isinstance(item, dict):
                raw_date = item.get("date") or item.get("update_date")
                if isinstance(raw_date, str):
                    raw_date = date.fromisoformat(raw_date[:10])
                out.append(
                    HistoryPoint(
                        date=raw_date,
                        physical_progress_pct=float(
                            item.get("physical_progress_pct", 0)
                        ),
                        expenditure_cr=float(item.get("expenditure_cr", 0)),
                    )
                )
        return out

    def _velocity(self, start_v: float, end_v: float, start_d: date, end_d: date) -> float:
        days = max((end_d - start_d).days, 1)
        return ((end_v - start_v) / days) * 30.0  # units per 30 days

    def _insights(
        self,
        prog_v: float,
        exp_v: float,
        efficiency: float,
        late_prog: float,
        trend: str,
    ) -> list[str]:
        notes: list[str] = []
        if prog_v < -15:
            notes.append(f"Physical progress has slowed by {abs(prog_v):.0f}% versus the earlier window.")
        elif prog_v > 15:
            notes.append(f"Physical progress velocity has improved by {prog_v:.0f}%.")
        if exp_v > 15:
            notes.append(f"Expenditure is accelerating ({exp_v:+.0f}%) relative to the first half of the series.")
        if exp_v > 8 and prog_v < 0:
            notes.append("Spend is rising while physical progress is losing speed — efficiency is leaking.")
        if efficiency < 0.6:
            notes.append("Cost efficiency is weak: each crore is buying less physical progress than expected.")
        elif efficiency > 1.1:
            notes.append("Cost efficiency is healthy — progress is keeping pace with spend.")
        if late_prog <= 0.05:
            notes.append("Recent reporting periods show near-zero physical progress (possible stall).")
        if trend == "IMPROVING":
            notes.append("Recent updates indicate the project is recovering trajectory.")
        if not notes:
            notes.append("Trend is broadly stable across the available reporting window.")
        return notes[:5]
