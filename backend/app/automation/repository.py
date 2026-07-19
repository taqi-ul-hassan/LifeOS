from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import AutomationRule, Execution, ExecutionLog


class AutomationRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: str, rule_id: str) -> AutomationRule | None:
        return self.session.scalar(
            select(AutomationRule).where(
                AutomationRule.id == rule_id, AutomationRule.user_id == user_id
            )
        )

    def list(self, user_id: str) -> list[AutomationRule]:
        return list(
            self.session.scalars(
                select(AutomationRule).where(AutomationRule.user_id == user_id)
            )
        )

    def executions(self, user_id: str) -> list[Execution]:
        return list(
            self.session.scalars(
                select(Execution)
                .where(Execution.user_id == user_id)
                .order_by(Execution.created_at.desc())
            )
        )

    def logs(self, user_id: str) -> list[ExecutionLog]:
        return list(
            self.session.scalars(
                select(ExecutionLog)
                .join(Execution, ExecutionLog.execution_id == Execution.id)
                .where(Execution.user_id == user_id)
            )
        )
