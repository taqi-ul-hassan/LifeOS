import os
import time
from fastapi import APIRouter
from sqlalchemy import text
from ..db import engine

router = APIRouter(prefix="/v1/system", tags=["system"])
started = time.time()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/readiness")
def readiness():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ready", "database": "ok"}
    except Exception:
        return {"status": "not_ready", "database": "unavailable"}


@router.get("/liveness")
def liveness():
    return {"status": "alive"}


@router.get("/metrics")
def metrics():
    return {"uptime_seconds": round(time.time() - started, 2)}


@router.get("/status")
def status():
    return {"pid": os.getpid(), "uptime_seconds": round(time.time() - started, 2)}


@router.get("/version")
def version():
    return {"service": "lifeos-api", "version": "0.11.0"}
