from typing import Any
from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator
from pgvector.sqlalchemy import Vector
from ..models import KnowledgeGraphEdge as KnowledgeEdge
from ..models import KnowledgeGraphNode as KnowledgeNode
from ..models import Memory, Timestamped, uid

__all__ = [
    "Memory",
    "KnowledgeNode",
    "KnowledgeEdge",
    "MemoryEmbedding",
    "MemoryTag",
    "MemoryReference",
    "ConversationMemory",
    "JournalMemory",
    "ObservationMemory",
    "DecisionMemory",
    "LearningMemory",
    "HealthMemory",
    "FinanceMemory",
    "RelationshipMemory",
    "ProjectMemory",
    "DocumentMemory",
]


class EmbeddingVector(TypeDecorator):
    """Uses pgvector in PostgreSQL and JSON in SQLite tests/local development."""

    impl = JSON
    cache_ok = True

    def __init__(self, dimensions: int = 64):
        super().__init__()
        self.dimensions = dimensions

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(
            Vector(self.dimensions) if dialect.name == "postgresql" else JSON()
        )


class MemoryEmbedding(Timestamped):
    __tablename__ = "memory_embeddings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    memory_id: Mapped[str] = mapped_column(
        ForeignKey("memories.id"), unique=True, index=True
    )
    provider: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))
    dimensions: Mapped[int] = mapped_column()
    embedding: Mapped[list[float]] = mapped_column(EmbeddingVector(64))


class MemoryTag(Timestamped):
    __tablename__ = "memory_tags"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    memory_id: Mapped[str] = mapped_column(ForeignKey("memories.id"), index=True)
    name: Mapped[str] = mapped_column(String(80), index=True)


class MemoryReference(Timestamped):
    __tablename__ = "memory_references"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    memory_id: Mapped[str] = mapped_column(ForeignKey("memories.id"), index=True)
    referenced_memory_id: Mapped[str] = mapped_column(
        ForeignKey("memories.id"), index=True
    )
    relation: Mapped[str] = mapped_column(String(80), default="related_to")
    evidence: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class _TypedMemory(Timestamped):
    __abstract__ = True
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    memory_id: Mapped[str] = mapped_column(
        ForeignKey("memories.id"), unique=True, index=True
    )
    attributes: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class ConversationMemory(_TypedMemory):
    __tablename__ = "conversation_memories"


class JournalMemory(_TypedMemory):
    __tablename__ = "journal_memories"


class ObservationMemory(_TypedMemory):
    __tablename__ = "observation_memories"


class DecisionMemory(_TypedMemory):
    __tablename__ = "decision_memories"


class LearningMemory(_TypedMemory):
    __tablename__ = "learning_memories"


class HealthMemory(_TypedMemory):
    __tablename__ = "health_memories"


class FinanceMemory(_TypedMemory):
    __tablename__ = "finance_memories"


class RelationshipMemory(_TypedMemory):
    __tablename__ = "relationship_memories"


class ProjectMemory(_TypedMemory):
    __tablename__ = "project_memories"


class DocumentMemory(_TypedMemory):
    __tablename__ = "document_memories"
