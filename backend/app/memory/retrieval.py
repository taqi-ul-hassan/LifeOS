from datetime import datetime, timezone
import math
from .repository import MemoryRepository
from .schemas import MemorySearch, RetrievedMemory, RetrievalResponse


def cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return 0
    denominator = math.sqrt(sum(v * v for v in left)) * math.sqrt(
        sum(v * v for v in right)
    )
    return sum(a * b for a, b in zip(left, right)) / denominator if denominator else 0


class Retriever:
    def __init__(self, repository: MemoryRepository):
        self.repository = repository

    def retrieve(
        self, user_id: str, query: MemorySearch, query_embedding: list[float]
    ) -> RetrievalResponse:
        candidates = []
        for memory in self.repository.list(user_id):
            if memory.archived or (
                query.memory_types and memory.memory_type not in query.memory_types
            ):
                continue
            tags = self.repository.tags(memory.id)
            if query.tags and not set(query.tags).intersection(tags):
                continue
            embedding = self.repository.embedding(memory.id)
            semantic = cosine(query_embedding, embedding.embedding) if embedding else 0
            keyword = sum(
                word in memory.content.lower() or word in memory.title.lower()
                for word in query.query.lower().split()
            ) / max(1, len(query.query.split()))
            age = max(
                0,
                1
                - min(
                    (
                        datetime.now(timezone.utc)
                        - memory.updated_at.replace(tzinfo=timezone.utc)
                    ).days,
                    365,
                )
                / 365,
            )
            score = (
                0.55 * semantic
                + 0.2 * keyword
                + 0.15 * memory.importance_score
                + 0.1 * age
            )
            if score >= query.min_similarity:
                candidates.append((score, memory, tags))
        ranked = sorted(candidates, key=lambda item: item[0], reverse=True)[
            : query.top_k
        ]
        memories = [
            RetrievedMemory(
                id=m.id,
                title=m.title,
                content=m.content,
                memory_type=m.memory_type,
                importance_score=m.importance_score,
                confidence=m.confidence,
                source=m.source,
                archived=m.archived,
                created_at=m.created_at,
                tags=tags,
                similarity=round(score, 4),
                citation=f"[memory:{m.id}] {m.title}",
            )
            for score, m, tags in ranked
        ]
        context = "\n".join(f"{item.citation}\n{item.content}" for item in memories)
        return RetrievalResponse(memories=memories, context=context)
