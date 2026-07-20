from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..config import get_settings
from ..db import get_session
from ..models import User
from ..dependencies import current_user
from .schemas import (
    MemoryCreate,
    MemoryRead,
    MemorySearch,
    MemoryStats,
    MemoryUpdate,
    RetrievalResponse,
)
from .service import MemoryService

router = APIRouter(prefix="/v1/memory", tags=["memory"])


def service(session: Session = Depends(get_session)) -> MemoryService:
    return MemoryService(session, get_settings())


@router.post("", response_model=MemoryRead, status_code=201)
async def create_memory(
    data: MemoryCreate,
    user: User = Depends(current_user),
    memory: MemoryService = Depends(service),
):
    return await memory.create(user.id, data)


@router.get("", response_model=list[MemoryRead])
def list_memories(
    user: User = Depends(current_user), memory: MemoryService = Depends(service)
):
    return [memory.read(item) for item in memory.repo.list(user.id)]


@router.get("/stats", response_model=MemoryStats)
def stats(user: User = Depends(current_user), memory: MemoryService = Depends(service)):
    return memory.stats(user.id)


@router.post("/search", response_model=RetrievalResponse)
async def search(
    data: MemorySearch,
    user: User = Depends(current_user),
    memory: MemoryService = Depends(service),
):
    return await _retrieve_memories(user, data, memory)


@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve(
    data: MemorySearch,
    user: User = Depends(current_user),
    memory: MemoryService = Depends(service),
):
    return await _retrieve_memories(user, data, memory)


async def _retrieve_memories(
    user: User, data: MemorySearch, memory: MemoryService
) -> RetrievalResponse:
    """Shared implementation for the legacy search alias and retrieve endpoint."""
    return await memory.retrieve(user.id, data)


@router.post("/consolidate")
def consolidate(
    user: User = Depends(current_user), memory: MemoryService = Depends(service)
):
    return {"archived": memory.consolidate(user.id)}


@router.post("/summarize")
def summarize(
    user: User = Depends(current_user), memory: MemoryService = Depends(service)
):
    return {
        "summary": " ".join(
            item.content for item in memory.repo.list(user.id) if not item.archived
        )[:2000]
    }


@router.get("/{memory_id}", response_model=MemoryRead)
def get_memory(
    memory_id: str,
    user: User = Depends(current_user),
    memory: MemoryService = Depends(service),
):
    return memory.get(user.id, memory_id)


@router.patch("/{memory_id}", response_model=MemoryRead)
def update_memory(
    memory_id: str,
    data: MemoryUpdate,
    user: User = Depends(current_user),
    memory: MemoryService = Depends(service),
):
    return memory.update(user.id, memory_id, data)


@router.delete("/{memory_id}", status_code=204)
def delete_memory(
    memory_id: str,
    user: User = Depends(current_user),
    memory: MemoryService = Depends(service),
):
    memory.archive(user.id, memory_id)
