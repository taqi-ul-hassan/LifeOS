from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..config import get_settings
from ..db import get_session
from ..dependencies import current_user
from ..automation.event_bus import event_bus
from ..automation.events import Event
from ..memory.service import MemoryService
from ..models import User
from .context import ContextEngine
from .decision import DecisionEngine
from .planning import PlanningEngine
from .recommendations import RecommendationEngine
from .reflection import ReflectionEngine
from .schemas import (
    PlanResponse,
    RecommendationsResponse,
    ReviewRequest,
    ReviewResponse,
    UnifiedContext,
)

router = APIRouter(tags=["life-engine"])


async def context_for(user: User, session: Session) -> UnifiedContext:
    return await ContextEngine(session, MemoryService(session, get_settings())).build(
        user.id
    )


@router.get("/v1/context", response_model=UnifiedContext)
async def context(
    user: User = Depends(current_user), session: Session = Depends(get_session)
):
    return await context_for(user, session)


@router.post("/v1/planning/daily", response_model=PlanResponse)
async def daily(
    user: User = Depends(current_user), session: Session = Depends(get_session)
):
    plan = PlanningEngine(session).plan(
        user.id, await context_for(user, session), "daily"
    )
    event_bus.publish(Event("LifePlanCreated", user.id, {"horizon": "daily"}))
    return plan


@router.post("/v1/planning/weekly", response_model=PlanResponse)
async def weekly(
    user: User = Depends(current_user), session: Session = Depends(get_session)
):
    plan = PlanningEngine(session).plan(
        user.id, await context_for(user, session), "weekly"
    )
    event_bus.publish(Event("LifePlanCreated", user.id, {"horizon": "weekly"}))
    return plan


@router.post("/v1/planning/review", response_model=ReviewResponse)
def review(
    data: ReviewRequest,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    result = ReflectionEngine(session).review(user.id, data.period)
    event_bus.publish(Event("ReflectionGenerated", user.id, {"period": data.period}))
    return result


@router.post("/v1/planning/recommend", response_model=RecommendationsResponse)
async def recommend(
    user: User = Depends(current_user), session: Session = Depends(get_session)
):
    context = await context_for(user, session)
    suggestions = DecisionEngine().recommend(context) + RecommendationEngine(
        session
    ).generate(user.id)
    result = RecommendationsResponse(
        recommendations=sorted(suggestions, key=lambda item: item.priority)
    )
    event_bus.publish(
        Event(
            "RecommendationGenerated", user.id, {"count": len(result.recommendations)}
        )
    )
    return result
