from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_session
from ..dependencies import current_user
from ..models import User
from .metrics import summary
from .repository import AutomationRepository
from .schemas import (
    AutomationCreate,
    AutomationMetrics,
    AutomationParse,
    AutomationRead,
    AutomationRun,
    AutomationUpdate,
)
from .service import AutomationService

router = APIRouter(prefix="/v1/automation", tags=["automation"])


def read(rule) -> AutomationRead:
    return AutomationRead(
        id=rule.id,
        name=rule.name,
        enabled=rule.enabled,
        definition=rule.definition,
        created_at=rule.created_at,
    )


def execution_read(execution) -> dict:
    return {
        "id": execution.id,
        "status": execution.status,
        "idempotency_key": execution.idempotency_key,
        "output": execution.output,
    }


def _run_rule(
    session: Session, user_id: str, rule_id: str, data: AutomationRun
) -> dict:
    return execution_read(
        AutomationService(session).run(
            user_id, rule_id, data.payload, data.idempotency_key
        )
    )


@router.post("", response_model=AutomationRead, status_code=201)
def create(
    data: AutomationCreate,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    return read(AutomationService(session).create(user.id, data))


@router.get("", response_model=list[AutomationRead])
def list_rules(
    user: User = Depends(current_user), session: Session = Depends(get_session)
):
    return [read(rule) for rule in AutomationRepository(session).list(user.id)]


@router.get("/history")
def history(
    user: User = Depends(current_user), session: Session = Depends(get_session)
):
    return [
        execution_read(item)
        for item in AutomationRepository(session).executions(user.id)
    ]


@router.get("/logs")
def logs(user: User = Depends(current_user), session: Session = Depends(get_session)):
    return AutomationRepository(session).logs(user.id)


@router.get("/metrics", response_model=AutomationMetrics)
def metrics(
    user: User = Depends(current_user), session: Session = Depends(get_session)
):
    return summary(AutomationRepository(session), user.id)


@router.post("/parse")
def parsed(
    data: AutomationParse,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    return AutomationService(session).parsed(data.text)


@router.post("/test")
def test_root(
    data: AutomationRun,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    if not data.rule_id:
        from fastapi import HTTPException

        raise HTTPException(422, "rule_id is required")
    return _run_rule(session, user.id, data.rule_id, data)


@router.post("/run")
def run_root(
    data: AutomationRun,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    if not data.rule_id:
        from fastapi import HTTPException

        raise HTTPException(422, "rule_id is required")
    return _run_rule(session, user.id, data.rule_id, data)


@router.post("/{rule_id}/test")
def test(
    rule_id: str,
    data: AutomationRun,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    return _run_rule(session, user.id, rule_id, data)


@router.post("/{rule_id}/run")
def run(
    rule_id: str,
    data: AutomationRun,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    return _run_rule(session, user.id, rule_id, data)


@router.get("/{rule_id}", response_model=AutomationRead)
def get(
    rule_id: str,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    item = AutomationRepository(session).get(user.id, rule_id)
    if not item:
        from fastapi import HTTPException

        raise HTTPException(404, "Automation not found")
    return read(item)


@router.patch("/{rule_id}", response_model=AutomationRead)
def update(
    rule_id: str,
    data: AutomationUpdate,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    return read(AutomationService(session).update(user.id, rule_id, data))


@router.delete("/{rule_id}", status_code=204)
def delete(
    rule_id: str,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    AutomationService(session).delete(user.id, rule_id)
