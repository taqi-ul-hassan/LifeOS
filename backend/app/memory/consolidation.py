from .repository import MemoryRepository
from .summarizer import MemorySummarizer


class Consolidator:
    def __init__(self, repository: MemoryRepository):
        self.repository, self.summarizer = repository, MemorySummarizer()

    def run(self, user_id: str) -> int:
        seen, archived = {}, 0
        for memory in self.repository.list(user_id):
            fingerprint = " ".join(memory.content.lower().split())
            if fingerprint in seen and not memory.archived:
                memory.archived = True
                archived += 1
            else:
                seen[fingerprint] = memory.id
        self.repository.session.commit()
        return archived
