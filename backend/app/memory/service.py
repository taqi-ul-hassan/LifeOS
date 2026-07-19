from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..config import Settings
from ..models import Memory
from .consolidation import Consolidator
from .embeddings import build_embedding_providers
from .models import MemoryEmbedding
from .repository import MemoryRepository
from .retrieval import Retriever
from .scorer import ImportanceScorer
from .schemas import (
    MemoryCreate,
    MemoryRead,
    MemorySearch,
    MemoryStats,
    MemoryUpdate,
    RetrievalResponse,
)


class MemoryService:
    def __init__(self, session: Session, settings: Settings):
        self.session, self.settings, self.repo = (
            session,
            settings,
            MemoryRepository(session),
        )
        self.providers = build_embedding_providers(settings)
        self.scorer = ImportanceScorer()

    def provider(self):
        provider = self.providers.get(self.settings.embedding_default_provider)
        if not provider:
            raise HTTPException(503, "Configured embedding provider is unavailable")
        return provider

    def read(self, memory: Memory) -> MemoryRead:
        return MemoryRead(
            id=memory.id,
            title=memory.title,
            content=memory.content,
            memory_type=memory.memory_type,
            importance_score=memory.importance_score,
            confidence=memory.confidence,
            source=memory.source,
            archived=memory.archived,
            created_at=memory.created_at,
            tags=self.repo.tags(memory.id),
        )

    async def create(self, user_id: str, data: MemoryCreate) -> MemoryRead:
        embedding_provider = self.provider()
        vector = await embedding_provider.embed(data.content)
        memory = self.repo.add(
            Memory(
                user_id=user_id,
                title=data.title,
                content=data.content,
                layer="long_term",
                memory_type=data.memory_type,
                source=data.source,
                source_type=data.source,
                confidence=data.confidence,
                importance_score=self.scorer.score(data.content, data.metadata),
                metadata_=data.metadata,
            )
        )
        self.repo.replace_tags(memory.id, data.tags)
        self.session.add(
            MemoryEmbedding(
                memory_id=memory.id,
                provider=embedding_provider.name,
                model=embedding_provider.model,
                dimensions=len(vector),
                embedding=vector,
            )
        )
        self.session.commit()
        self.session.refresh(memory)
        return self.read(memory)

    def get(self, user_id: str, memory_id: str) -> MemoryRead:
        memory = self.repo.get(user_id, memory_id)
        if not memory:
            raise HTTPException(404, "Memory not found")
        return self.read(memory)

    def update(self, user_id: str, memory_id: str, data: MemoryUpdate) -> MemoryRead:
        memory = self.repo.get(user_id, memory_id)
        if not memory:
            raise HTTPException(404, "Memory not found")
        for field, value in data.model_dump(
            exclude_unset=True, exclude={"tags"}
        ).items():
            setattr(memory, field, value)
        if data.tags is not None:
            self.repo.replace_tags(memory.id, data.tags)
        self.session.commit()
        self.session.refresh(memory)
        return self.read(memory)

    def archive(self, user_id: str, memory_id: str) -> None:
        memory = self.repo.get(user_id, memory_id)
        if not memory:
            raise HTTPException(404, "Memory not found")
        memory.archived = True
        self.session.commit()

    async def retrieve(self, user_id: str, query: MemorySearch) -> RetrievalResponse:
        return Retriever(self.repo).retrieve(
            user_id, query, await self.provider().embed(query.query)
        )

    def consolidate(self, user_id: str) -> int:
        return Consolidator(self.repo).run(user_id)

    def stats(self, user_id: str) -> MemoryStats:
        memories = self.repo.list(user_id)
        return MemoryStats(
            total=len(memories),
            active=sum(not m.archived for m in memories),
            archived=sum(m.archived for m in memories),
            by_type=self.repo.stats(user_id),
        )
