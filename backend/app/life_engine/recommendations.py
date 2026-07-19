from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import LearningSession, Project, Task
from .schemas import Recommendation


class RecommendationEngine:
    def __init__(self, session: Session):
        self.session = session

    def generate(self, user_id: str) -> list[Recommendation]:
        results = []
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        last_learning = self.session.scalar(
            select(LearningSession)
            .where(LearningSession.user_id == user_id)
            .order_by(LearningSession.started_at.desc())
        )
        if not last_learning or last_learning.started_at < now - timedelta(days=3):
            results.append(
                Recommendation(
                    category="learning",
                    message="You have not logged learning in 3 days.",
                    reason="A short practice session maintains continuity.",
                    priority=2,
                )
            )
        due = list(
            self.session.scalars(
                select(Project).where(
                    Project.user_id == user_id,
                    Project.due_at.is_not(None),
                    Project.due_at <= now + timedelta(days=7),
                    Project.status == "active",
                )
            )
        )
        results += [
            Recommendation(
                category="deadline",
                message=f"{project.name} is approaching its deadline.",
                reason="Deadline is within seven days.",
                priority=1,
            )
            for project in due
        ]
        open_tasks = list(
            self.session.scalars(
                select(Task).where(Task.user_id == user_id, Task.status != "completed")
            )
        )
        if len(open_tasks) > 8:
            results.append(
                Recommendation(
                    category="workload",
                    message="Your workload is high.",
                    reason=f"{len(open_tasks)} tasks remain open; narrow the plan.",
                    priority=1,
                )
            )
        return results
