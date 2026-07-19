from .repository import AutomationRepository


def summary(repository: AutomationRepository, user_id: str) -> dict:
    executions = repository.executions(user_id)
    return {
        "executions": len(executions),
        "succeeded": sum(item.status == "succeeded" for item in executions),
        "failed": sum(item.status == "failed" for item in executions),
    }
