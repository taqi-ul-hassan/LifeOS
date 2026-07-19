from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..memory.schemas import MemorySearch
from ..memory.service import MemoryService
from ..models import CalendarEvent, Goal, HealthMetric, Project, Task
from .schemas import UnifiedContext


class ContextEngine:
    def __init__(self, session: Session, memory: MemoryService):
        self.session, self.memory = session, memory

    async def build(self, user_id: str) -> UnifiedContext:
        tasks = list(
            self.session.scalars(
                select(Task)
                .where(Task.user_id == user_id, Task.status != "completed")
                .order_by(Task.priority, Task.due_at)
            )
        )
        goals = list(
            self.session.scalars(
                select(Goal).where(Goal.user_id == user_id, Goal.status == "active")
            )
        )
        project = (
            self.session.get(Project, tasks[0].project_id)
            if tasks and tasks[0].project_id
            else None
        )
        now = datetime.now(timezone.utc)
        events = list(
            self.session.scalars(
                select(CalendarEvent).where(
                    CalendarEvent.user_id == user_id,
                    CalendarEvent.starts_at >= now.replace(tzinfo=None),
                    CalendarEvent.starts_at
                    <= (now + timedelta(hours=8)).replace(tzinfo=None),
                )
            )
        )
        latest_energy = self.session.scalar(
            select(HealthMetric)
            .where(
                HealthMetric.user_id == user_id,
                HealthMetric.metric_type.in_(["energy", "mood"]),
            )
            .order_by(HealthMetric.measured_at.desc())
        )
        energy = min(1, max(0, (latest_energy.value / 10) if latest_energy else 0.7))
        retrieved = await self.memory.retrieve(
            user_id,
            MemorySearch(
                query="current priorities goals workload", top_k=4, min_similarity=0.12
            ),
        )
        available = max(
            0,
            480
            - sum(
                max(0, int((event.ends_at - event.starts_at).total_seconds() / 60))
                for event in events
            ),
        )
        return UnifiedContext(
            current_task=tasks[0].title if tasks else None,
            current_project=project.name if project else None,
            active_goals=[goal.title for goal in goals],
            available_minutes=available,
            energy_level=energy,
            recent_activity=[task.title for task in tasks[:5]],
            calendar_events=[event.title for event in events],
            memory_context=retrieved.context,
        )
