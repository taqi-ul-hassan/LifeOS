from datetime import datetime, timezone
from uuid import uuid4
from .schemas import EventEnvelope


class EventBus:
    """Transactional outbox boundary. Replace InMemoryEventBus with Kafka/NATS adapter in deployment."""

    def publish(
        self, event_type: str, actor_id: str, aggregate_id: str, payload: dict
    ) -> EventEnvelope:
        raise NotImplementedError


class InMemoryEventBus(EventBus):
    def __init__(self):
        self.events: list[EventEnvelope] = []

    def publish(
        self, event_type: str, actor_id: str, aggregate_id: str, payload: dict
    ) -> EventEnvelope:
        event = EventEnvelope(
            id=str(uuid4()),
            type=event_type,
            occurred_at=datetime.now(timezone.utc),
            actor_id=actor_id,
            aggregate_id=aggregate_id,
            payload=payload,
        )
        self.events.append(event)
        return event


event_bus = InMemoryEventBus()
