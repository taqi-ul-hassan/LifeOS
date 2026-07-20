from sqlalchemy import select
from ..models import FinancialRecord, HealthMetric


class Intelligence:
    def __init__(self, s):
        self.s = s

    def health(self, u):
        return list(
            self.s.scalars(
                select(HealthMetric)
                .where(HealthMetric.user_id == u)
                .order_by(HealthMetric.measured_at.desc())
            )
        )

    def finance(self, u):
        return list(
            self.s.scalars(
                select(FinancialRecord)
                .where(FinancialRecord.user_id == u)
                .order_by(FinancialRecord.occurred_on.desc())
            )
        )

    def scores(self, u):
        h = self.health(u)
        f = self.finance(u)
        values = {x.metric_type: x.value for x in h[:30]}
        sleep = min(100, values.get("sleep_hours", 7) * 12.5)
        water = min(100, values.get("water_glasses", 8) * 12.5)
        fitness = min(100, values.get("steps", 8000) / 80)
        health = round((sleep + water + fitness) / 3)
        income = sum(x.amount for x in f if x.record_type == "income")
        expense = sum(x.amount for x in f if x.record_type == "expense")
        financial = round(
            max(0, min(100, 50 + (income - expense) / (income or 1) * 50))
        )
        return {
            "health_score": health,
            "fitness_score": round(fitness),
            "productivity_score": round((health + fitness) / 2),
            "financial_health_score": financial,
            "consistency_score": round((health + financial) / 2),
            "goal_progress_score": 50,
            "overall_life_score": round((health + financial) / 2),
        }

    def forecast(self, u):
        f = self.finance(u)
        income = sum(x.amount for x in f if x.record_type == "income")
        expense = sum(x.amount for x in f if x.record_type == "expense")
        return {
            "projected_balance": round(income - expense, 2),
            "cash_shortage_risk": income < expense,
            "savings_opportunity": round(max(0, income - expense) * 0.2, 2),
            "budget_overrun_risk": expense > income,
        }

    def alerts(self, u):
        h = self.health(u)
        out = []
        latest = {x.metric_type: x.value for x in h[:20]}
        if latest.get("sleep_hours", 8) < 6:
            out.append(
                {"category": "health", "message": "Poor sleep detected", "priority": 1}
            )
        if self.forecast(u)["budget_overrun_risk"]:
            out.append(
                {
                    "category": "finance",
                    "message": "Spending exceeds income",
                    "priority": 1,
                }
            )
        return out

    def report(self, u, area):
        return {
            "area": area,
            "scores": self.scores(u),
            "forecast": self.forecast(u),
            "alerts": self.alerts(u),
            "recommendations": [
                "Protect sleep and schedule one focused block.",
                "Review discretionary spending this week.",
            ],
        }
