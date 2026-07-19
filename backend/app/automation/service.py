from fastapi import HTTPException
from sqlalchemy.orm import Session
from .executor import Executor
from .models import AutomationAudit, AutomationRule
from .parser import parse
from .repository import AutomationRepository
from .schemas import AutomationCreate, AutomationUpdate


class AutomationService:
    def __init__(self, session: Session):
        self.session, self.repo = session, AutomationRepository(session)

    def create(self, user_id: str, data: AutomationCreate) -> AutomationRule:
        rule = AutomationRule(
            user_id=user_id,
            name=data.name,
            enabled=data.enabled,
            definition={
                "trigger": data.trigger,
                "conditions": data.conditions,
                "actions": data.actions,
            },
        )
        self.session.add(rule)
        self.session.flush()
        self.session.add(
            AutomationAudit(
                user_id=user_id,
                action="created",
                target_id=rule.id,
                detail=rule.definition,
            )
        )
        self.session.commit()
        self.session.refresh(rule)
        return rule

    def update(
        self, user_id: str, rule_id: str, data: AutomationUpdate
    ) -> AutomationRule:
        rule = self.repo.get(user_id, rule_id)
        if not rule:
            raise HTTPException(404, "Automation not found")
        if data.name is not None:
            rule.name = data.name
        if data.enabled is not None:
            rule.enabled = data.enabled
        definition = rule.definition.copy()
        for key in ("trigger", "conditions", "actions"):
            value = getattr(data, key)
            if value is not None:
                definition[key] = value
        rule.definition = definition
        self.session.commit()
        self.session.refresh(rule)
        return rule

    def delete(self, user_id: str, rule_id: str) -> None:
        rule = self.repo.get(user_id, rule_id)
        if not rule:
            raise HTTPException(404, "Automation not found")
        rule.enabled = False
        self.session.add(
            AutomationAudit(user_id=user_id, action="disabled", target_id=rule.id)
        )
        self.session.commit()

    def run(self, user_id: str, rule_id: str, payload: dict, key: str | None = None):
        rule = self.repo.get(user_id, rule_id)
        if not rule or not rule.enabled:
            raise HTTPException(404, "Enabled automation not found")
        return Executor(self.session).run(
            rule,
            user_id,
            payload,
            key or f"manual:{rule_id}:{len(self.repo.executions(user_id))}",
        )

    def parsed(self, text: str) -> dict:
        return parse(text)
