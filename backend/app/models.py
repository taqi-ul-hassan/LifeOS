import uuid
from datetime import date, datetime, timezone
from typing import Any
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


def uid() -> str: return str(uuid.uuid4())
def now() -> datetime: return datetime.now(timezone.utc)


class Timestamped(Base):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now, nullable=False)


class User(Timestamped):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile: Mapped["Profile"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)
    tasks: Mapped[list["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    goals: Mapped[list["Goal"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Profile(Timestamped):
    __tablename__ = "profiles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    display_name: Mapped[str] = mapped_column(String(120))
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    user: Mapped[User] = relationship(back_populates="profile")


class Project(Timestamped):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(200)); description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="active"); due_at: Mapped[datetime | None] = mapped_column(DateTime)


class Goal(Timestamped):
    __tablename__ = "goals"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(300)); horizon: Mapped[str] = mapped_column(String(30), default="quarter")
    status: Mapped[str] = mapped_column(String(30), default="active"); target_date: Mapped[date | None] = mapped_column(Date)
    progress: Mapped[float] = mapped_column(Float, default=0)
    user: Mapped[User] = relationship(back_populates="goals")


class Task(Timestamped):
    __tablename__ = "tasks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id")); goal_id: Mapped[str | None] = mapped_column(ForeignKey("goals.id"))
    title: Mapped[str] = mapped_column(String(300)); status: Mapped[str] = mapped_column(String(30), default="open")
    priority: Mapped[int] = mapped_column(Integer, default=3); due_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime); metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    user: Mapped[User] = relationship(back_populates="tasks")


class Habit(Timestamped):
    __tablename__ = "habits"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); name: Mapped[str] = mapped_column(String(120))
    cadence: Mapped[str] = mapped_column(String(40)); target: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict); active: Mapped[bool] = mapped_column(Boolean, default=True)

class CalendarEvent(Timestamped):
    __tablename__ = "calendar_events"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); title: Mapped[str] = mapped_column(String(300)); starts_at: Mapped[datetime] = mapped_column(DateTime); ends_at: Mapped[datetime] = mapped_column(DateTime)
    provider: Mapped[str | None] = mapped_column(String(40)); external_id: Mapped[str | None] = mapped_column(String(200), index=True); attendees: Mapped[list] = mapped_column(JSON, default=list)

class Note(Timestamped):
    __tablename__ = "notes"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); title: Mapped[str] = mapped_column(String(300)); content: Mapped[str] = mapped_column(Text); project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"))

class Document(Timestamped):
    __tablename__ = "documents"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); filename: Mapped[str] = mapped_column(String(512)); storage_key: Mapped[str] = mapped_column(String(512), unique=True); mime_type: Mapped[str] = mapped_column(String(120)); checksum: Mapped[str] = mapped_column(String(128)); extracted_text: Mapped[str | None] = mapped_column(Text)

class Memory(Timestamped):
    __tablename__ = "memories"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); layer: Mapped[str] = mapped_column(String(30)); content: Mapped[str] = mapped_column(Text); importance: Mapped[float] = mapped_column(Float, default=0.5); confidence: Mapped[float] = mapped_column(Float, default=1); embedding_ref: Mapped[str | None] = mapped_column(String(100)); source_type: Mapped[str] = mapped_column(String(50)); expires_at: Mapped[datetime | None] = mapped_column(DateTime)

class JournalEntry(Timestamped):
    __tablename__ = "journal_entries"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); entry_date: Mapped[date] = mapped_column(Date, default=date.today); content: Mapped[str] = mapped_column(Text); mood: Mapped[int | None] = mapped_column(Integer); tags: Mapped[list] = mapped_column(JSON, default=list)

class AIObservation(Timestamped):
    __tablename__ = "ai_observations"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); agent: Mapped[str] = mapped_column(String(80)); category: Mapped[str] = mapped_column(String(80)); content: Mapped[str] = mapped_column(Text); confidence: Mapped[float] = mapped_column(Float); requires_approval: Mapped[bool] = mapped_column(Boolean, default=False); acted_on_at: Mapped[datetime | None] = mapped_column(DateTime)

class Notification(Timestamped):
    __tablename__ = "notifications"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); channel: Mapped[str] = mapped_column(String(30)); title: Mapped[str] = mapped_column(String(200)); body: Mapped[str] = mapped_column(Text); read_at: Mapped[datetime | None] = mapped_column(DateTime); scheduled_for: Mapped[datetime | None] = mapped_column(DateTime)

class HealthMetric(Timestamped):
    __tablename__ = "health_metrics"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); metric_type: Mapped[str] = mapped_column(String(60)); value: Mapped[float] = mapped_column(Float); unit: Mapped[str] = mapped_column(String(30)); measured_at: Mapped[datetime] = mapped_column(DateTime); source: Mapped[str] = mapped_column(String(50), default="manual")

class LearningSession(Timestamped):
    __tablename__ = "learning_sessions"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); topic: Mapped[str] = mapped_column(String(200)); started_at: Mapped[datetime] = mapped_column(DateTime); minutes: Mapped[int] = mapped_column(Integer); outcome: Mapped[str | None] = mapped_column(Text)

class FinancialRecord(Timestamped):
    __tablename__ = "financial_records"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); record_type: Mapped[str] = mapped_column(String(30)); amount: Mapped[float] = mapped_column(Float); currency: Mapped[str] = mapped_column(String(3)); occurred_on: Mapped[date] = mapped_column(Date); category: Mapped[str | None] = mapped_column(String(80)); merchant: Mapped[str | None] = mapped_column(String(200)); metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)

class Relationship(Timestamped):
    __tablename__ = "relationships"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); name: Mapped[str] = mapped_column(String(200)); relationship_type: Mapped[str] = mapped_column(String(80)); birthday: Mapped[date | None] = mapped_column(Date); last_contact_at: Mapped[datetime | None] = mapped_column(DateTime); notes: Mapped[str | None] = mapped_column(Text)

class KnowledgeGraphNode(Timestamped):
    __tablename__ = "knowledge_graph_nodes"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); label: Mapped[str] = mapped_column(String(300)); node_type: Mapped[str] = mapped_column(String(80)); attributes: Mapped[dict] = mapped_column(JSON, default=dict)

class KnowledgeGraphEdge(Timestamped):
    __tablename__ = "knowledge_graph_edges"; id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); source_id: Mapped[str] = mapped_column(ForeignKey("knowledge_graph_nodes.id")); target_id: Mapped[str] = mapped_column(ForeignKey("knowledge_graph_nodes.id")); relation: Mapped[str] = mapped_column(String(100)); weight: Mapped[float] = mapped_column(Float, default=1); evidence: Mapped[dict] = mapped_column(JSON, default=dict)

class OAuthAccount(Timestamped):
    __tablename__ = "oauth_accounts"; __table_args__ = (UniqueConstraint("provider", "provider_account_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); provider: Mapped[str] = mapped_column(String(50)); provider_account_id: Mapped[str] = mapped_column(String(255)); access_token_encrypted: Mapped[str | None] = mapped_column(Text); refresh_token_encrypted: Mapped[str | None] = mapped_column(Text)
