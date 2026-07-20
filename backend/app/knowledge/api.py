from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_session
from ..dependencies import current_user
from ..models import User, KnowledgeGraphNode, KnowledgeGraphEdge
from .engine import Knowledge

router = APIRouter(prefix="/v1/knowledge", tags=["knowledge"])


@router.post("/import")
def import_(
    data: dict, user: User = Depends(current_user), s: Session = Depends(get_session)
):
    n = Knowledge(s).import_(
        user.id, data["title"], data["content"], data.get("type", "resource")
    )
    return {"id": n.id, "label": n.label}


@router.get("/search")
def search(
    q: str, user: User = Depends(current_user), s: Session = Depends(get_session)
):
    return Knowledge(s).search(user.id, q)


@router.get("/graph")
def graph(user: User = Depends(current_user), s: Session = Depends(get_session)):
    return {
        "nodes": list(s.query(KnowledgeGraphNode).filter_by(user_id=user.id)),
        "edges": list(s.query(KnowledgeGraphEdge).filter_by(user_id=user.id)),
    }


@router.get("/mastery")
def mastery(user: User = Depends(current_user), s: Session = Depends(get_session)):
    return Knowledge(s).mastery(user.id)


@router.post("/quiz")
def quiz(
    data: dict, user: User = Depends(current_user), s: Session = Depends(get_session)
):
    return Knowledge(s).quiz(user.id, data["topic"])


@router.post("/flashcards")
def cards(
    data: dict, user: User = Depends(current_user), s: Session = Depends(get_session)
):
    return Knowledge(s).cards(user.id, data["topic"])


@router.get("/recommendations")
def recommendations(
    user: User = Depends(current_user), s: Session = Depends(get_session)
):
    return {"recommendations": [Knowledge(s).path(user.id)]}


@router.post("/summary")
def summary(
    data: dict, user: User = Depends(current_user), s: Session = Depends(get_session)
):
    return {
        "summary": " ".join(
            str(n.attributes.get("content", ""))
            for n in Knowledge(s).search(user.id, data["topic"])
        )[:2000]
    }


@router.get("/learning-path")
def path(user: User = Depends(current_user), s: Session = Depends(get_session)):
    return Knowledge(s).path(user.id)
