"""Add persistent memory engine and pgvector-compatible embedding tables."""

from alembic import op
import sqlalchemy as sa
from app.memory import models as memory_models

revision = "20260719_0002"
down_revision = "20260719_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    existing = {column["name"] for column in sa.inspect(bind).get_columns("memories")}
    additions = [
        (
            "title",
            sa.Column(
                "title",
                sa.String(300),
                nullable=False,
                server_default="Untitled memory",
            ),
        ),
        (
            "memory_type",
            sa.Column(
                "memory_type", sa.String(30), nullable=False, server_default="semantic"
            ),
        ),
        (
            "importance_score",
            sa.Column(
                "importance_score", sa.Float(), nullable=False, server_default="0.5"
            ),
        ),
        (
            "source",
            sa.Column("source", sa.String(50), nullable=False, server_default="user"),
        ),
        (
            "archived",
            sa.Column(
                "archived", sa.Boolean(), nullable=False, server_default=sa.false()
            ),
        ),
        (
            "metadata",
            sa.Column("metadata", sa.JSON(), nullable=False, server_default="{}"),
        ),
    ]
    for name, column in additions:
        if name not in existing:
            op.add_column("memories", column)
    for table in [
        memory_models.MemoryEmbedding.__table__,
        memory_models.MemoryTag.__table__,
        memory_models.MemoryReference.__table__,
        memory_models.ConversationMemory.__table__,
        memory_models.JournalMemory.__table__,
        memory_models.ObservationMemory.__table__,
        memory_models.DecisionMemory.__table__,
        memory_models.LearningMemory.__table__,
        memory_models.HealthMemory.__table__,
        memory_models.FinanceMemory.__table__,
        memory_models.RelationshipMemory.__table__,
        memory_models.ProjectMemory.__table__,
        memory_models.DocumentMemory.__table__,
    ]:
        table.create(bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for table in [
        memory_models.DocumentMemory.__table__,
        memory_models.ProjectMemory.__table__,
        memory_models.RelationshipMemory.__table__,
        memory_models.FinanceMemory.__table__,
        memory_models.HealthMemory.__table__,
        memory_models.LearningMemory.__table__,
        memory_models.DecisionMemory.__table__,
        memory_models.ObservationMemory.__table__,
        memory_models.JournalMemory.__table__,
        memory_models.ConversationMemory.__table__,
        memory_models.MemoryReference.__table__,
        memory_models.MemoryTag.__table__,
        memory_models.MemoryEmbedding.__table__,
    ]:
        table.drop(bind, checkfirst=True)
