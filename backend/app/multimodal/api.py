from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import current_user
from ..models import User
from ..automation.event_bus import event_bus
from ..automation.events import Event
from .service import Multimodal

router = APIRouter(tags=["multimodal"])


def run(kind, data, user):
    try:
        service = Multimodal()
        result = getattr(service, kind)(data)
        event_bus.publish(Event("SystemStarted", user.id, {"multimodal": kind}))
        return result
    except (KeyError, ValueError) as e:
        raise HTTPException(422, str(e))


@router.post("/v1/voice/transcribe")
def voice(data: dict, user: User = Depends(current_user)):
    return run("transcribe", data, user)


@router.post("/v1/voice/speak")
def speak(data: dict, user: User = Depends(current_user)):
    return run("speak", data, user)


@router.post("/v1/image/analyze")
def image(data: dict, user: User = Depends(current_user)):
    return run("image", data, user)


@router.post("/v1/image/ocr")
def ocr(data: dict, user: User = Depends(current_user)):
    return {"text": run("image", data, user)["ocr_text"]}


@router.post("/v1/document/analyze")
def document(data: dict, user: User = Depends(current_user)):
    return run("document", data, user)


@router.post("/v1/audio/transcribe")
def audio(data: dict, user: User = Depends(current_user)):
    return run("transcribe", data, user)


@router.post("/v1/video/analyze")
def video(data: dict, user: User = Depends(current_user)):
    return run("video", data, user)


@router.post("/v1/multimodal/chat")
def chat(data: dict, user: User = Depends(current_user)):
    return {
        "response": data.get("message", ""),
        "context": "Use AI orchestrator provider for generated multimodal responses.",
    }


@router.post("/v1/multimodal/import")
def import_(data: dict, user: User = Depends(current_user)):
    return run("document", data, user)


@router.get("/v1/multimodal/history")
def history(user: User = Depends(current_user)):
    return []
