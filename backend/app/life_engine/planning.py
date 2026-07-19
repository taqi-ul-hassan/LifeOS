from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Task
from .schemas import PlanItem, PlanResponse, UnifiedContext


class PlanningEngine:
    def __init__(self, session: Session):
        self.session = session

    def plan(self, user_id: str, context: UnifiedContext, horizon: str) -> PlanResponse:
        tasks = list(
            self.session.scalars(
                select(Task)
                .where(Task.user_id == user_id, Task.status != "completed")
                .order_by(Task.priority, Task.due_at)
            )
        )
        budget = (
            context.available_minutes
            if horizon == "daily"
            else context.available_minutes * 5
        )
        items = []
        for task in tasks:
            if budget < 25:
                break
            minutes = 50 if task.priority <= 2 and context.energy_level >= 0.45 else 25
            budget -= minutes
            reason = (
                "High priority and aligned to current workload"
                if task.priority <= 2
                else "Best available next action"
            )
            items.append(
                PlanItem(
                    task_id=task.id,
                    title=task.title,
                    priority=task.priority,
                    recommended_minutes=minutes,
                    reason=reason,
                )
            )
        focus = [item for item in items if item.recommended_minutes >= 50][:2]
        return PlanResponse(
            horizon=horizon,
            context=context,
            items=items,
            focus_sessions=focus,
            explanation="Plan is recalculated from open tasks, calendar capacity, energy, active goals, and relevant memory.",
        )
