from fastapi import APIRouter, Depends
from datetime import date, datetime
from sqlalchemy.orm import Session
from ..db import get_session
from ..dependencies import current_user
from ..models import User, HealthMetric, FinancialRecord
from .engine import Intelligence

router = APIRouter(tags=["intelligence"])


@router.get("/v1/health")
def health(user: User = Depends(current_user), s: Session = Depends(get_session)):
    return Intelligence(s).health(user.id)


@router.post("/v1/health")
def add_health(
    data: dict, user: User = Depends(current_user), s: Session = Depends(get_session)
):
    x = HealthMetric(
        user_id=user.id,
        metric_type=data["metric_type"],
        value=data["value"],
        unit=data.get("unit", "unit"),
        measured_at=data.get("measured_at") or datetime.utcnow(),
    )
    s.add(x)
    s.commit()
    return {"id": x.id}


@router.get("/v1/health/report")
def health_report(
    user: User = Depends(current_user), s: Session = Depends(get_session)
):
    return Intelligence(s).report(user.id, "health")


@router.get("/v1/health/score")
def health_score(user: User = Depends(current_user), s: Session = Depends(get_session)):
    return Intelligence(s).scores(user.id)


@router.get("/v1/finance")
def finance(user: User = Depends(current_user), s: Session = Depends(get_session)):
    return Intelligence(s).finance(user.id)


@router.post("/v1/finance")
def add_finance(
    data: dict, user: User = Depends(current_user), s: Session = Depends(get_session)
):
    x = FinancialRecord(
        user_id=user.id,
        record_type=data["record_type"],
        amount=data["amount"],
        currency=data.get("currency", "USD"),
        occurred_on=data.get("occurred_on", date.today()),
        category=data.get("category"),
    )
    s.add(x)
    s.commit()
    return {"id": x.id}


@router.get("/v1/finance/report")
def finance_report(
    user: User = Depends(current_user), s: Session = Depends(get_session)
):
    return Intelligence(s).report(user.id, "finance")


@router.get("/v1/finance/forecast")
def forecast(user: User = Depends(current_user), s: Session = Depends(get_session)):
    return Intelligence(s).forecast(user.id)


@router.get("/v1/life/report")
def life_report(user: User = Depends(current_user), s: Session = Depends(get_session)):
    return Intelligence(s).report(user.id, "life")
