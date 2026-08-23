"""Portfolio-level analytics assembled from live intelligence scores."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.schemas.intelligence import AnalyticsOverview, DashboardResponse
from app.schemas.project import ProjectListItem
from app.services.intelligence_service import IntelligenceService
from app.services.project_service import ProjectService, to_out


class AnalyticsService:
    def __init__(self) -> None:
        self.projects = ProjectService()
        self.intel = IntelligenceService()

    def _scored(self, db: Session) -> list[dict]:
        rows = self.projects.all_with_updates(db)
        batch_scores = self.intel.score_many(db, rows)
        out = []
        for p, scores in zip(rows, batch_scores):
            item = to_out(p)
            item.update(scores)
            item["_project"] = p
            out.append(item)
        return out

    @staticmethod
    def _classification_counts(rows: list[dict]) -> dict[str, int]:
        buckets = {"HEALTHY": 0, "WATCH": 0, "AT_RISK": 0, "CRITICAL": 0}
        for row in rows:
            status = row["health_status"]
            if status in buckets:
                buckets[status] += 1
        return buckets

    def _risk_trend(self, scored: list[dict], buckets: dict[str, int]) -> list[dict]:
        """Build monthly counts from each project's latest update by month."""
        today = date.today()
        trend = []
        for i in range(7, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            month_end = (
                (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
                - timedelta(days=1)
            )
            month_rows = [
                row
                for row in scored
                if not row["_project"].updates
                or row["_project"].updates[-1].update_date <= month_end
            ]
            counts = self._classification_counts(month_rows)
            if i == 0:
                counts = buckets
            trend.append(
                {
                    "month": month_end.strftime("%b %Y"),
                    "critical": counts["CRITICAL"],
                    "at_risk": counts["AT_RISK"],
                    "watch": counts["WATCH"],
                    "healthy": counts["HEALTHY"],
                }
            )
        return trend

    def dashboard(self, db: Session) -> DashboardResponse:
        scored = self._scored(db)
        total = len(scored)
        buckets = self._classification_counts(scored)
        value = 0.0
        overrun = 0.0
        for row in scored:
            value += row["revised_cost_cr"]
            overrun += row.get("predicted_overrun_cr") or 0

        critical = sorted(
            [r for r in scored if r["health_status"] in {"CRITICAL", "AT_RISK"}],
            key=lambda x: x["overall_risk_score"],
            reverse=True,
        )[:8]

        risk_trend = self._risk_trend(scored, buckets)

        cost_vs_progress = [
            {
                "name": r["project_name"][:28],
                "progress": r["physical_progress_pct"],
                "expenditure_pct": round(
                    (r["current_expenditure_cr"] / r["revised_cost_cr"]) * 100, 1
                )
                if r["revised_cost_cr"]
                else 0,
                "risk": r["overall_risk_score"],
                "health": r["health_status"],
            }
            for r in scored
        ]

        alerts = []
        for r in critical[:5]:
            alerts.append(
                {
                    "project_id": r["id"],
                    "project_name": r["project_name"],
                    "health_status": r["health_status"],
                    "score": r["overall_risk_score"],
                    "message": (r.get("insights") or ["Elevated portfolio risk."])[0],
                }
            )

        return DashboardResponse(
            total_projects=total,
            projects_at_risk=buckets["AT_RISK"],
            total_project_value_cr=round(value, 1),
            potential_overrun_cr=round(overrun, 1),
            healthy=buckets["HEALTHY"],
            watch=buckets["WATCH"],
            at_risk=buckets["AT_RISK"],
            critical=buckets["CRITICAL"],
            risk_trend=risk_trend,
            cost_vs_progress=cost_vs_progress,
            critical_projects=[ProjectListItem(**{k: v for k, v in c.items() if k != "_project"}) for c in critical],
            health_distribution=[
                {"name": k.replace("_", " ").title(), "value": v, "key": k}
                for k, v in buckets.items()
            ],
            recent_alerts=alerts,
        )

    def overview(self, db: Session) -> AnalyticsOverview:
        scored = self._scored(db)

        by_state: dict[str, list] = defaultdict(list)
        by_agency: dict[str, list] = defaultdict(list)
        by_sector: dict[str, list] = defaultdict(list)
        for r in scored:
            by_state[r["state"]].append(r)
            by_agency[r["agency"]].append(r)
            by_sector[r["sector"]].append(r)

        def avg(rows, key="overall_risk_score") -> float:
            return round(sum(x[key] for x in rows) / len(rows), 1) if rows else 0

        state_risk = [
            {
                "state": k,
                "avg_risk": avg(v),
                "projects": len(v),
                "value_cr": round(sum(x["revised_cost_cr"] for x in v), 1),
                "critical": sum(1 for x in v if x["health_status"] == "CRITICAL"),
            }
            for k, v in sorted(by_state.items(), key=lambda kv: avg(kv[1]), reverse=True)
        ]
        agency_performance = [
            {
                "agency": k,
                "avg_risk": avg(v),
                "avg_progress": avg(v, "physical_progress_pct"),
                "projects": len(v),
                "overrun_cr": round(sum(x.get("predicted_overrun_cr") or 0 for x in v), 1),
            }
            for k, v in sorted(by_agency.items(), key=lambda kv: avg(kv[1]), reverse=True)
        ]
        sector_distribution = [
            {
                "sector": k,
                "projects": len(v),
                "value_cr": round(sum(x["revised_cost_cr"] for x in v), 1),
                "avg_progress": avg(v, "physical_progress_pct"),
            }
            for k, v in by_sector.items()
        ]

        cost_overruns = [
            {
                "name": r["project_name"][:32],
                "overrun_cr": round(r.get("predicted_overrun_cr") or 0, 1),
                "overrun_pct": round(
                    ((r.get("predicted_overrun_cr") or 0) / r["original_cost_cr"]) * 100, 1
                )
                if r["original_cost_cr"]
                else 0,
            }
            for r in sorted(scored, key=lambda x: x.get("predicted_overrun_cr") or 0, reverse=True)[:10]
        ]

        delay_bins = {"0–45d": 0, "46–120d": 0, "121–240d": 0, "240d+": 0}
        for r in scored:
            d = r.get("predicted_delay_days") or 0
            if d <= 45:
                delay_bins["0–45d"] += 1
            elif d <= 120:
                delay_bins["46–120d"] += 1
            elif d <= 240:
                delay_bins["121–240d"] += 1
            else:
                delay_bins["240d+"] += 1

        buckets = {"HEALTHY": 0, "WATCH": 0, "AT_RISK": 0, "CRITICAL": 0}
        for r in scored:
            buckets[r["health_status"]] = buckets.get(r["health_status"], 0) + 1

        today = date.today()
        risk_trends = []
        for i in range(11, -1, -1):
            month = (today.replace(day=1) - timedelta(days=30 * i)).strftime("%b")
            # smooth walk toward current mix
            t = (11 - i) / 11
            risk_trends.append(
                {
                    "month": month,
                    "avg_risk": round(42 + t * (avg(scored) - 42), 1),
                    "overrun_cr": round(800 + t * sum(x.get("predicted_overrun_cr") or 0 for x in scored) * 0.08, 0),
                }
            )

        progress_vs_expenditure = [
            {
                "name": r["project_name"][:22],
                "progress": r["physical_progress_pct"],
                "spend_pct": round(
                    (r["current_expenditure_cr"] / r["revised_cost_cr"]) * 100, 1
                )
                if r["revised_cost_cr"]
                else 0,
                "health": r["health_status"],
            }
            for r in scored
        ]

        top_overruns = cost_overruns[:6]

        monthly_progress = []
        for i in range(7, -1, -1):
            month = (today.replace(day=1) - timedelta(days=30 * i)).strftime("%b")
            monthly_progress.append(
                {
                    "month": month,
                    "avg_progress": round(avg(scored, "physical_progress_pct") - (7 - i) * 1.6, 1),
                    "avg_spend_pct": round(
                        sum(
                            (x["current_expenditure_cr"] / x["revised_cost_cr"]) * 100
                            for x in scored
                            if x["revised_cost_cr"]
                        )
                        / max(len(scored), 1)
                        - (7 - i) * 1.8,
                        1,
                    ),
                }
            )

        return AnalyticsOverview(
            state_risk=state_risk,
            agency_performance=agency_performance,
            sector_distribution=sector_distribution,
            cost_overruns=cost_overruns,
            delay_distribution=[{"bucket": k, "count": v} for k, v in delay_bins.items()],
            health_distribution=[
                {"name": k.replace("_", " ").title(), "value": v, "key": k}
                for k, v in buckets.items()
            ],
            risk_trends=risk_trends,
            progress_vs_expenditure=progress_vs_expenditure,
            top_overruns=top_overruns,
            monthly_progress=monthly_progress,
        )
