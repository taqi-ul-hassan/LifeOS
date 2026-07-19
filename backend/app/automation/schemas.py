from datetime import datetime
from pydantic import BaseModel, Field


class AutomationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    trigger: dict
    conditions: dict = {}
    actions: list[dict] = Field(min_length=1)
    enabled: bool = True


class AutomationUpdate(BaseModel):
    name: str | None = None
    enabled: bool | None = None
    trigger: dict | None = None
    conditions: dict | None = None
    actions: list[dict] | None = None


class AutomationRead(BaseModel):
    id: str
    name: str
    enabled: bool
    definition: dict
    created_at: datetime


class AutomationRun(BaseModel):
    rule_id: str | None = None
    idempotency_key: str | None = None
    payload: dict = {}


class AutomationParse(BaseModel):
    text: str = Field(min_length=3, max_length=1000)


class AutomationMetrics(BaseModel):
    executions: int
    succeeded: int
    failed: int
