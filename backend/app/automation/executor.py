from sqlalchemy.orm import Session
from .actions import execute
from .conditions import evaluate
from .models import Execution, ExecutionHistory


class Executor:
    def __init__(self, session: Session):
        self.session = session

    def run(self, rule, user_id: str, payload: dict, idempotency_key: str) -> Execution:
        existing = (
            self.session.query(Execution)
            .filter_by(rule_id=rule.id, idempotency_key=idempotency_key)
            .one_or_none()
        )
        if existing:
            return existing
        execution = Execution(
            user_id=user_id,
            rule_id=rule.id,
            idempotency_key=idempotency_key,
            status="running",
            input=payload,
        )
        self.session.add(execution)
        self.session.flush()
        try:
            if rule.definition.get("conditions") and not evaluate(
                rule.definition["conditions"], payload
            ):
                execution.status = "skipped"
                execution.output = {"reason": "conditions_not_met"}
            else:
                execution.output = {
                    "results": [
                        execute(self.session, user_id, execution.id, action, payload)
                        for action in rule.definition.get("actions", [])
                    ]
                }
                execution.status = "succeeded"
        except Exception as error:
            execution.status = "failed"
            execution.output = {"error": str(error)}
        self.session.add(
            ExecutionHistory(
                execution_id=execution.id,
                status=execution.status,
                detail=str(execution.output),
            )
        )
        self.session.commit()
        return execution
