from .models import SyncRecord


def record(session, connection, mode, result):
    item = SyncRecord(
        connection_id=connection.id,
        mode=mode,
        status=result["status"],
        cursor=result.get("cursor"),
        detail=result,
    )
    session.add(item)
    return item
