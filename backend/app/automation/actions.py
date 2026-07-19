from sqlalchemy.orm import Session
from ..models import Task
from .models import AutomationNotification, ExecutionLog


def execute(
    session: Session, user_id: str, execution_id: str, action: dict, payload: dict
) -> dict:
    action_type = action.get("type")
    if action_type == "create_task":
        task = Task(
            user_id=user_id, title=action["title"], priority=action.get("priority", 3)
        )
        session.add(task)
        result = {"task_id": task.id, "type": "create_task"}
    elif action_type == "notify_user":
        session.add(
            AutomationNotification(
                user_id=user_id,
                message=action.get("message", "Automation notification"),
            )
        )
        result = {"type": "notify_user"}
    elif action_type in {
        "log_activity",
        "generate_summary",
        "generate_reflection",
        "create_recommendation",
        "execute_ai_agent",
        "execute_workflow",
        "schedule_reminder",
        "update_task",
        "delete_task",
        "archive_task",
        "create_memory",
        "update_memory",
    }:
        result = {"type": action_type, "status": "accepted", "payload": payload}
    else:
        raise ValueError(f"Unsupported action: {action_type}")
    session.add(
        ExecutionLog(
            execution_id=execution_id,
            level="info",
            message=f"Executed {action_type}",
            payload=result,
        )
    )
    return result
