from collections import deque


class RetryQueueStore:
    def __init__(self):
        self.items = deque()

    def push(self, item: dict) -> None:
        self.items.append(item)

    def pop(self) -> dict | None:
        return self.items.popleft() if self.items else None
