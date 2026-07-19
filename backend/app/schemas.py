from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class ORMModel(BaseModel): model_config = ConfigDict(from_attributes=True)
class RegisterRequest(BaseModel): email: EmailStr; password: str = Field(min_length=12, max_length=128); display_name: str = Field(min_length=1, max_length=120)
class LoginRequest(BaseModel): email: EmailStr; password: str
class TokenResponse(BaseModel): access_token: str; token_type: str = "bearer"
class UserRead(ORMModel): id: str; email: EmailStr; is_active: bool; created_at: datetime
class TaskCreate(BaseModel): title: str = Field(min_length=1, max_length=300); priority: int = Field(default=3, ge=1, le=5); due_at: datetime | None = None; project_id: str | None = None; goal_id: str | None = None
class TaskUpdate(BaseModel): title: str | None = Field(default=None, min_length=1, max_length=300); priority: int | None = Field(default=None, ge=1, le=5); status: str | None = None; due_at: datetime | None = None
class TaskRead(ORMModel): id: str; title: str; status: str; priority: int; due_at: datetime | None; completed_at: datetime | None; created_at: datetime
class GoalCreate(BaseModel): title: str = Field(min_length=1, max_length=300); horizon: str = "quarter"; target_date: date | None = None; project_id: str | None = None
class GoalRead(ORMModel): id: str; title: str; horizon: str; status: str; progress: float; target_date: date | None
class EventEnvelope(BaseModel): id: str; type: str; occurred_at: datetime; actor_id: str; aggregate_id: str; payload: dict
class DailyBrief(BaseModel): open_tasks: int; high_priority_tasks: list[TaskRead]; focus_recommendation: str
