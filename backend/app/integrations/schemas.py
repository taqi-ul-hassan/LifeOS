from pydantic import BaseModel, Field


class ConnectRequest(BaseModel):
    provider: str
    scopes: list[str] = []
    credentials: dict = Field(default_factory=dict)


class ConnectionRead(BaseModel):
    id: str
    provider: str
    status: str
    scopes: list[str]
    metadata: dict


class SyncRequest(BaseModel):
    mode: str = "manual"
    cursor: str | None = None
