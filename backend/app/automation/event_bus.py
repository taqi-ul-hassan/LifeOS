from collections import defaultdict
from collections.abc import Callable
from .events import Event


class EventBus:
    def __init__(self):
        self.subscribers: dict[str, list[Callable[[Event], None]]] = defaultdict(list)
        self.published: list[Event] = []

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self.subscribers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        self.published.append(event)
        for handler in self.subscribers[event.type]:
            handler(event)


event_bus = EventBus()
