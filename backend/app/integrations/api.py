from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_session
from ..dependencies import current_user
from ..models import User
from .registry import registry
from .schemas import ConnectRequest, ConnectionRead, SyncRequest
from .service import IntegrationService

router = APIRouter(prefix="/v1/integrations", tags=["integrations"])


def read(item):
    return ConnectionRead(
        id=item.id,
        provider=item.provider,
        status=item.status,
        scopes=item.scopes,
        metadata=item.metadata_,
    )


@router.post("/connect", response_model=ConnectionRead)
def connect(
    data: ConnectRequest,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    return read(
        IntegrationService(session).connect(
            user.id, data.provider, data.scopes, data.credentials
        )
    )


@router.post("/disconnect")
def disconnect(
    data: ConnectRequest,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    IntegrationService(session).disconnect(user.id, data.provider)
    return {"status": "disconnected"}


@router.get("", response_model=list[ConnectionRead])
def list_connections(
    user: User = Depends(current_user), session: Session = Depends(get_session)
):
    return [read(item) for item in IntegrationService(session).repo.list(user.id)]


@router.get("/status")
def status(user: User = Depends(current_user), session: Session = Depends(get_session)):
    return {
        "connections": [
            read(item) for item in IntegrationService(session).repo.list(user.id)
        ]
    }


@router.get("/health")
def health(user: User = Depends(current_user)):
    return {
        item["name"]: registry.get(item["name"]).health()
        for item in registry.discover()
    }


@router.post("/{provider}/sync")
def sync(
    provider: str,
    data: SyncRequest,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    return IntegrationService(session).sync(user.id, provider, data.mode, data.cursor)


@router.get("/{provider}", response_model=ConnectionRead)
def get(
    provider: str,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
):
    from fastapi import HTTPException

    item = IntegrationService(session).repo.get(user.id, provider)
    if not item:
        raise HTTPException(404, "Connection not found")
    return read(item)
