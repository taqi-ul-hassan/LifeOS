def evaluate(expression: dict, payload: dict) -> bool:
    operator = expression.get("op", "equals").lower()
    if operator == "and":
        return all(evaluate(item, payload) for item in expression.get("items", []))
    if operator == "or":
        return any(evaluate(item, payload) for item in expression.get("items", []))
    if operator == "not":
        return not evaluate(expression.get("item", {}), payload)
    value = payload.get(expression.get("field"))
    expected = expression.get("value")
    if operator == "equals":
        return value == expected
    if operator == "contains":
        return (
            expected in (value or [])
            if not isinstance(value, str)
            else str(expected) in value
        )
    if operator == "greater_than":
        return value is not None and value > expected
    if operator == "less_than":
        return value is not None and value < expected
    if operator in {
        "tag_match",
        "goal_status",
        "project_status",
        "memory_importance",
        "user_context",
        "date_comparison",
    }:
        return value == expected
    return False
