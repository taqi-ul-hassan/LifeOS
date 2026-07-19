from datetime import datetime
from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=20_000)
    memory_type: str = "semantic"
    source: str = "user"
    confidence: float = Field(default=1, ge=0, le=1)
    tags: list[str] = Field(default_factory=list, max_length=20)
    metadata: dict = Field(default_factory=dict)


class MemoryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    content: str | None = Field(default=None, min_length=1, max_length=20_000)
    archived: bool | None = None
    tags: list[str] | None = None


class MemoryRead(BaseModel):
    id: str
    title: str
    content: str
    memory_type: str
    importance_score: float
    confidence: float
    source: str
    archived: bool
    created_at: datetime
    tags: list[str] = []


class MemorySearch(BaseModel):
    query: str = Field(min_length=1, max_length=8_000)
    top_k: int = Field(default=8, ge=1, le=30)
    memory_types: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    min_similarity: float = Field(default=0, ge=0, le=1)


class RetrievedMemory(MemoryRead):
    similarity: float
    citation: str


class RetrievalResponse(BaseModel):
    memories: list[RetrievedMemory]
    context: str


class MemoryStats(BaseModel):
    total: int
    active: int
    archived: int
    by_type: dict[str, int]
