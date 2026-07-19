from __future__ import annotations
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..models import Memory
from .models import MemoryEmbedding, MemoryReference, MemoryTag


class MemoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: str, memory_id: str) -> Memory | None:
        return self.session.scalar(
            select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        )

    def list(self, user_id: str) -> list[Memory]:
        return list(
            self.session.scalars(
                select(Memory)
                .where(Memory.user_id == user_id)
                .order_by(Memory.updated_at.desc())
            )
        )

    def add(self, memory: Memory) -> Memory:
        self.session.add(memory)
        self.session.flush()
        return memory

    def tags(self, memory_id: str) -> list[str]:
        return list(
            self.session.scalars(
                select(MemoryTag.name).where(MemoryTag.memory_id == memory_id)
            )
        )

    def replace_tags(self, memory_id: str, tags: list[str]) -> None:
        self.session.query(MemoryTag).filter_by(memory_id=memory_id).delete()
        self.session.add_all(
            [
                MemoryTag(memory_id=memory_id, name=tag.lower().strip())
                for tag in sorted(set(tags))
                if tag.strip()
            ]
        )

    def embedding(self, memory_id: str) -> MemoryEmbedding | None:
        return self.session.scalar(
            select(MemoryEmbedding).where(MemoryEmbedding.memory_id == memory_id)
        )

    def stats(self, user_id: str) -> dict[str, int]:
        return dict(
            self.session.execute(
                select(Memory.memory_type, func.count())
                .where(Memory.user_id == user_id)
                .group_by(Memory.memory_type)
            ).all()
        )


class KnowledgeRepository:
    def __init__(self, session: Session):
        self.session = session

    def link(self, memory_id: str, related_id: str) -> None:
        if memory_id != related_id:
            self.session.add(
                MemoryReference(
                    memory_id=memory_id,
                    referenced_memory_id=related_id,
                    relation="related_to",
                )
            )
