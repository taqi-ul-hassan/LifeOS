from pydantic import BaseModel, Field


class UnifiedContext(BaseModel):
    current_task: str | None
    current_project: str | None
    active_goals: list[str]
    available_minutes: int
    energy_level: float
    recent_activity: list[str]
    calendar_events: list[str]
    memory_context: str


class PlanItem(BaseModel):
    task_id: str
    title: str
    priority: int
    recommended_minutes: int
    reason: str


class PlanResponse(BaseModel):
    horizon: str
    context: UnifiedContext
    items: list[PlanItem]
    focus_sessions: list[PlanItem]
    explanation: str


class ReviewRequest(BaseModel):
    period: str = Field(pattern="^(daily|weekly|monthly)$")


class ReviewResponse(BaseModel):
    period: str
    wins: list[str]
    mistakes: list[str]
    progress: list[str]
    learning: list[str]
    health: list[str]
    productivity: list[str]
    goal_alignment: str


class Recommendation(BaseModel):
    category: str
    message: str
    reason: str
    priority: int


class RecommendationsResponse(BaseModel):
    recommendations: list[Recommendation]
