def parse(text: str) -> dict:
    normalized = text.lower()
    if "every friday" in normalized:
        return {
            "trigger": {"type": "cron", "expression": "0 9 * * FRI"},
            "conditions": {},
            "actions": [{"type": "generate_summary", "period": "weekly"}],
        }
    if "finish a project" in normalized:
        return {
            "trigger": {"type": "project", "event": "ProjectUpdated"},
            "conditions": {"op": "equals", "field": "status", "value": "completed"},
            "actions": [{"type": "generate_reflection"}],
        }
    if "haven't studied" in normalized or "haven't studied" in normalized:
        return {
            "trigger": {"type": "time", "every": "daily"},
            "conditions": {
                "op": "greater_than",
                "field": "days_since_learning",
                "value": 2,
            },
            "actions": [
                {"type": "notify_user", "message": "Time for a study session."}
            ],
        }
    return {
        "trigger": {"type": "manual"},
        "conditions": {},
        "actions": [{"type": "log_activity", "message": text}],
    }
