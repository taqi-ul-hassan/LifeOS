from .events import Event


def matches(trigger: dict, event: Event) -> bool:
    trigger_type = trigger.get("type", "manual").lower()
    if trigger_type in {"manual", "api"}:
        return True
    if trigger_type in {"task", "goal", "memory", "project", "journal", "system"}:
        return event.type.lower().startswith(trigger_type)
    return trigger_type in {"time", "cron"}
