from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Goal, HealthMetric, LearningSession, Task
from .schemas import ReviewResponse


class ReflectionEngine:
    def __init__(self, session: Session):
        self.session = session

    def review(self, user_id: str, period: str) -> ReviewResponse:
        tasks = list(self.session.scalars(select(Task).where(Task.user_id == user_id)))
        goals = list(
            self.session.scalars(
                select(Goal).where(Goal.user_id == user_id, Goal.status == "active")
            )
        )
        completed = [task.title for task in tasks if task.status == "completed"]
        learning = list(
            self.session.scalars(
                select(LearningSession).where(LearningSession.user_id == user_id)
            )
        )
        health = list(
            self.session.scalars(
                select(HealthMetric)
                .where(HealthMetric.user_id == user_id)
                .order_by(HealthMetric.measured_at.desc())
                .limit(3)
            )
        )
        return ReviewResponse(
            period=period,
            wins=completed[:5] or ["No completed tasks recorded."],
            mistakes=["Review unfinished work and remove stale commitments."]
            if any(task.status != "completed" for task in tasks)
            else [],
            progress=[f"{goal.title}: {round(goal.progress * 100)}%" for goal in goals],
            learning=[
                f"{item.topic}: {item.minutes} minutes" for item in learning[-5:]
            ],
            health=[f"{item.metric_type}: {item.value} {item.unit}" for item in health],
            productivity=[f"{len(completed)} tasks completed"],
            goal_alignment="Current work is aligned when planned tasks support an active goal; add project/goal links to improve this signal.",
        )
