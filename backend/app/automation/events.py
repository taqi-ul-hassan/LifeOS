from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class Event:
    type: str
    user_id: str
    payload: dict
    id: str = ""
    occurred_at: datetime | None = None

    def __post_init__(self):
        object.__setattr__(self, "id", self.id or str(uuid4()))
        object.__setattr__(
            self, "occurred_at", self.occurred_at or datetime.now(timezone.utc)
        )


EVENT_TYPES = {
    "TaskCreated",
    "TaskCompleted",
    "GoalCreated",
    "GoalCompleted",
    "ProjectCreated",
    "ProjectUpdated",
    "MemoryCreated",
    "MemoryUpdated",
    "JournalCreated",
    "LifePlanCreated",
    "RecommendationGenerated",
    "ReflectionGenerated",
    "HealthUpdated",
    "FinanceUpdated",
    "SystemStarted",
    "UserLoggedIn",
}
