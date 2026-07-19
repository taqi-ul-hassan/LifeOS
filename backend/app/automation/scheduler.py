from datetime import datetime, timezone


def due(run_at: datetime, cancelled: bool = False) -> bool:
    return not cancelled and run_at <= datetime.now(timezone.utc).replace(tzinfo=None)
