import uuid
from typing import Any
from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..models import Timestamped


def uid() -> str:
    return str(uuid.uuid4())


class IntegrationConnection(Timestamped):
    __tablename__ = "integration_connections"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(30), default="disconnected")
    scopes: Mapped[list] = mapped_column(JSON, default=list)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)


class EncryptedCredential(Timestamped):
    __tablename__ = "encrypted_credentials"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    connection_id: Mapped[str] = mapped_column(
        ForeignKey("integration_connections.id"), unique=True, index=True
    )
    ciphertext: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[str | None] = mapped_column(String(64))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class WebhookDelivery(Timestamped):
    __tablename__ = "webhook_deliveries"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    provider: Mapped[str] = mapped_column(String(80))
    delivery_id: Mapped[str] = mapped_column(String(200), unique=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="received")


class SyncRecord(Timestamped):
    __tablename__ = "integration_sync_records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    connection_id: Mapped[str] = mapped_column(
        ForeignKey("integration_connections.id"), index=True
    )
    mode: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30))
    cursor: Mapped[str | None] = mapped_column(String(500))
    detail: Mapped[dict] = mapped_column(JSON, default=dict)


class IntegrationAudit(Timestamped):
    __tablename__ = "integration_audits"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(80))
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
